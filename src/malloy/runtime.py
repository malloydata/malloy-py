# Copyright 2023 Google LLC
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# runtime.py
"""Malloy runtime class for loading, compiling, and running .malloy files"""
from __future__ import annotations

import asyncio
import grpc
import hashlib
import json
import logging
import os
import re

from pathlib import Path

from malloy.data.connection import ConnectionInterface
from malloy.data.connection_manager import ConnectionManagerInterface, DefaultConnectionManager
from malloy.service import ServiceManager
from malloy.services.v1.compiler_pb2_grpc import CompilerStub
from malloy.services.v1.compiler_pb2 import CompileRequest, CompileDocument, CompilerRequest, SqlBlockSchema


class Runtime():
  """Malloy runtime class for loading, compiling, and running .malloy files"""
  ready_state = [grpc.ChannelConnectivity.READY]
  error_state = [grpc.ChannelConnectivity.TRANSIENT_FAILURE]

  default_connection = "default_connection"

  def __init__(
      self,
      connection_manager: ConnectionManagerInterface = DefaultConnectionManager(
      ),
      service_manager=ServiceManager()):
    self._log = logging.getLogger(__name__)
    self._connection_manager = connection_manager
    self._service_manager = service_manager
    self._was_entered = False
    self._log.debug("Runtime initialized")

  def __enter__(self):
    self._was_entered = True
    return self

  def __exit__(self, *ex):
    self._service_manager._kill_service()
    self._was_entered = False

  def add_connection(self, connection: ConnectionInterface) -> Runtime:
    """Add connection to use when referenced by malloy source files."""
    self._connection_manager.add_connection(connection)
    return self

  def load_file(self, file):
    self._is_file = True
    file_path = Path(file).resolve()
    self._file_dir = file_path.parent
    self._file_name = file_path
    self._log.debug("Loading file: %s", self._file_name)
    self._log.debug("  import_path: %s", self._file_dir)
    return self

  def load_source(self, source, import_path=None):
    self._is_file = False
    self._source = source
    if import_path is None:
      import_path = os.getcwd()
    self._file_dir = Path(import_path).resolve()
    self._file_name = Path(self._file_dir, "__inline-souce__.malloy")
    self._log.debug("Loading source: %s", source)
    self._log.debug("  import_path: %s", self._file_dir)
    self._log.debug("  file_name: %s", self._file_name)
    return self

  async def get_sql(self, named_query=None, query=None):
    self._sql = None
    if named_query is None and query is None:
      self._log.error("Parameter named_query or query is required to get_sql()")
      return

    service = await self._service_manager.get_service()

    if not self._service_manager.is_ready():
      self._log.error(
          "Service manager failed to report ready state, compile ending")
      return

    self._log.debug("Using compiler service: %s", service)
    self._init_compile_state(named_query=named_query, query=query)

    async with grpc.aio.insecure_channel(service) as channel:
      stub = CompilerStub(channel)
      self._response_stream = stub.CompileStream(self)
      state = channel.get_state()
      while state not in self.ready_state and state not in self.error_state:
        await channel.wait_for_state_change(state)
        state = channel.get_state()

      if state in self.ready_state:
        await self._compile_completed.wait()
      else:
        raise ValueError("Channel not in ready state", state)

    return self._sql

  async def run(self, connection, query=None, named_query=None):
    sql = await self.get_sql(query=query, named_query=named_query)
    self._log.debug(sql)
    if sql is None:
      return None

    return self._connection_manager.get_connection(connection).run_query(sql)

  def __aiter__(self):
    return self

  async def __anext__(self):
    if self._compile_completed.is_set():
      raise StopAsyncIteration
    try:
      if not self._first_request_sent:
        self._first_request_sent = True
        return self._generate_initial_compile_request()
    except Exception as ex:
      self._log.error(ex)
      self._compile_completed.set()
      raise StopAsyncIteration from ex

    while not self._compile_completed.is_set() and self._last_response is None:
      await self._parse_response()

    if self._compile_completed.is_set():
      raise StopAsyncIteration
    try:
      self._log.debug("Generating next request")
      if self._last_response.type == CompilerRequest.Type.IMPORT:
        self._log.debug("  generating IMPORT request")
        request = self._generate_import_request()
        self._last_response = None
        return request

      if self._last_response.type == CompilerRequest.Type.TABLE_SCHEMAS:
        self._log.debug("  generating TABLE_SCHEMAS request")
        request = self._generate_table_schema_request()
        self._last_response = None
        return request

      if self._last_response.type == CompilerRequest.Type.SQL_BLOCK_SCHEMAS:
        self._log.debug("  generating SQL_BLOCK_SCHEMAS request")
        request = self._generate_sql_block_schemas_request()
        self._last_response = None
        return request

    except Exception as ex:
      self._log.error(ex)
      self._compile_completed.set()
      raise StopAsyncIteration from ex

    self._compile_completed.set()
    raise StopAsyncIteration

  def _init_compile_state(self, named_query=None, query=None):
    self._compile_completed = asyncio.Event()
    self._compile_completed.clear()
    self._first_request_sent = False
    self._seen_responses = []
    self._last_response = None
    self._sql = None
    if named_query is None:
      self._query_type = "query"
      self._query = query
    else:
      self._query_type = "named"
      self._query = named_query

  def _generate_initial_compile_request(self):
    self._log.debug("Generating initial compile request")
    if self._is_file:
      compile_request = CompileRequest(type=CompileRequest.Type.COMPILE,
                                       document=self._create_document(
                                           self._file_name))
    else:
      compile_request = CompileRequest(type=CompileRequest.Type.COMPILE,
                                       document=self._create_document(
                                           self._file_name, internal=True))
    if self._query_type == "query":
      compile_request.query = self._query
    else:
      compile_request.named_query = self._query
    return compile_request

  def _generate_import_request(self):
    request = CompileRequest(type=CompileRequest.Type.REFERENCES)
    imports = []
    for url in self._last_response.import_urls:
      imports.append(self._create_document(url))
    request.references.extend(imports)
    self._log.debug(request)
    return request

  def _generate_table_schema_request(self):
    # Compiler should really be telling us which connection to use per table...
    tables_per_connection_to_fetch = {}
    self._log.debug("  requested table schemas:\n%s",
                    self._last_response.table_schemas)
    for table_schema in self._last_response.table_schemas:
      m = re.search(pattern=r"^(.+):(.+)$", string=table_schema)
      connection_name = m.group(1)
      table_name = table_schema

      if connection_name in tables_per_connection_to_fetch:
        tables_per_connection_to_fetch[connection_name].append(table_name)
      else:
        tables_per_connection_to_fetch[connection_name] = [table_name]

    # self._log.debug("  fetching table schemas:\n{}".format(
    #     tables_per_connection_to_fetch))
    combined_schemas = {"schemas": {}}
    for connection_name, tables in tables_per_connection_to_fetch.items():
      self._log.debug("  using connection: %s", connection_name)

      if connection_name == self.default_connection:
        connection_name = self._connection_manager.get_default_connection_name()
        self._log.debug("  default connection: %s", connection_name)

      connection = self._connection_manager.get_connection(connection_name)
      # tables = tables_per_connection_to_fetch.get(connection)
      self._log.debug("  tables: %s", tables)
      schemas = connection.get_schema_for_tables(tables)
      combined_schemas["schemas"] = {
          **combined_schemas["schemas"],
          **schemas["schemas"]
      }

    request = CompileRequest(type=CompileRequest.Type.TABLE_SCHEMAS,
                             schema=json.dumps(combined_schemas))
    self._log.debug(request)
    return request

  def _generate_sql_block_schemas_request(self):
    # Compiler should really be telling us which connection to use per table...
    self._log.debug(self._last_response.sql_block.sql)
    m = re.search(pattern=r"^md5:/(.+)//.+$",
                  string=self._last_response.sql_block.name)
    connection_name = m.group(1)
    self._log.debug("  fetching sql_block schema from connection: %s",
                    connection_name)
    connection = self._connection_manager.get_connection(connection_name)
    sql = self._last_response.sql_block.sql
    name = self._last_response.sql_block.name
    schema = connection.get_schema_for_sql_block(name, sql)
    self._log.debug("  schema:\n%s", json.dumps(schema))
    request = CompileRequest(type=CompileRequest.Type.SQL_BLOCK_SCHEMAS,
                             sql_block_schemas=[
                                 SqlBlockSchema(name=name,
                                                sql=sql,
                                                schema=json.dumps(schema))
                             ])
    return request

  def _create_document(self, path, internal=False):
    file_path = path
    if path != self._file_name:
      file_path = path.removeprefix(f"{self._file_name}/")
    url = f"mlr://{path}"
    if not internal:
      return CompileDocument(url=url,
                             content=Path(self._file_dir,
                                          file_path).read_text(encoding="utf8"))
    return CompileDocument(url=url, content=self._source)

  async def _parse_response(self):
    self._log.debug("Awaiting compiler response")
    self._last_response = await self._response_stream.read()
    if self._last_response is None:
      self._log.error("No response received, ending session")
      return

    last_response_hash = hashlib.md5(
        self._last_response.SerializeToString(deterministic=True)).digest()
    self._log.debug("Last Response ID: %s", last_response_hash)

    if last_response_hash in self._seen_responses:
      self._log.error("Request loop detected, ending session")
      self._compile_completed.set()
      return

    self._seen_responses.append(last_response_hash)

    if self._last_response.type == CompilerRequest.Type.COMPLETE:
      self._log.debug("Received compile COMPLETE, ending session")
      self._sql = self._last_response.content
      self._compile_completed.set()
      return

    if self._last_response.type == CompilerRequest.Type.UNKNOWN:
      self._log.info("Received response type UNKNOWN")
      self._log.error(self._last_response.content)
      self._compile_completed.set()
      return

    self._log.debug(self._last_response)
