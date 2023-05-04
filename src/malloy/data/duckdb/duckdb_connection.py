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

# duckdb_connection.py
"""Module contains a Malloy connection for DuckDb. """

from __future__ import annotations

from ..connection import ConnectionInterface
from collections.abc import Sequence
from pathlib import Path
import duckdb
import logging
import re


class DuckDbConnection(ConnectionInterface):
  """Basic implementation of a Malloy ConnectionInterface for DuckDb. """

  _table_regex = re.compile("^duckdb:(.+)$")

  def __init__(self, home_dir=None, name="duckdb"):
    self._log = logging.getLogger(f"{__name__}({name})")
    self._name = name
    self._client_options = None
    if home_dir is None:
      self._home_directory = None
    else:
      self._home_directory = Path(home_dir).resolve()
    self._con = None
    self._log.debug("DuckDbConnection(\"%s\") initialized", name)

  def get_name(self) -> str:
    return self._name

  def with_options(self, options) -> DuckDbConnection:
    self._client_options = options
    return self

  def with_home_dir(self, path) -> DuckDbConnection:
    self._home_directory = path
    return self

  def get_connection(self):
    if self._con is None:
      self._con = duckdb.connect(database=":memory:",
                                 config=self._client_options)
      if self._home_directory:
        sql = f"SET FILE_SEARCH_PATH=\"{self._home_directory}\""
        self._log.debug(sql)
        self._con.execute(sql)
    return self._con

  def get_schema_for_tables(self, tables: Sequence[str]):
    self._log.debug("Fetching schema for tables...")
    schema = {"schemas": {}}
    con = self.get_connection()
    for table in tables:
      table_name = table[table.find(":") + 1:]
      self._log.debug("Fetching %s", table_name)
      con.execute(f"DESCRIBE SELECT * FROM \"{table_name}\"")
      schema["schemas"][
          f"{self.get_name()}:{table_name}"] = self._to_struct_def(
              table_name, con.fetchall())
    return schema

  def run_query(self, sql: str):
    self._log.debug("Running Query:")
    self._log.debug(sql)
    con = self.get_connection()
    con.execute(sql)
    return con

  def _to_struct_def(self, table, schema):
    return {
        "type": "struct",
        "name": table,
        "dialect": "duckdb",
        "structSource": {
            "type": "table",
            "tablePath": table
        },
        "structRelationship": {
            "type": "basetable",
            "connectionName": "fake"
        },
        "fields": self._map_fields(schema)
    }

  def _map_fields(self, schema):
    fields = []
    for metadata in schema:
      field = {"name": metadata[0]}
      field_type = metadata[1]
      # DECIMAL type includes precision ex. DECIMAL(18,3)
      if field_type.startswith("DECIMAL"):
        field_type = "DECIMAL"
      if field_type in self.TYPE_MAP:
        field |= self.TYPE_MAP[field_type]
      else:
        self._log.warning("Field type not mapped: %s", field_type)
      fields.append(field)

    return fields

  TYPE_MAP = {
      "VARCHAR": {
          "type": "string"
      },
      "BIGINT": {
          "type": "number",
          "numberType": "integer"
      },
      "DOUBLE": {
          "type": "number",
          "numberType": "float"
      },
      "DATE": {
          "type": "date"
      },
      "TIMESTAMP": {
          "type": "timestamp"
      },
      "TIME": {
          "type": "string"
      },
      "DECIMAL": {
          "type": "number",
          "numberType": "float"
      },
      "BOOLEAN": {
          "type": "boolean"
      },
      "INTEGER": {
          "type": "number",
          "numberType": "integer"
      },
  }

  def get_schema_for_sql_block(self, name: str, sql: str):
    con = self.get_connection()
    con.execute(f"DESCRIBE SELECT * FROM ({sql})")
    return {
        "type": "struct",
        "dialect": "duckdb",
        "name": name,
        "structSource": {
            "type": "sql",
            "method": "subquery",
            # "sqlBlock": sqlRef,
        },
        "structRelationship": {
            "type": "basetable",
            "connectionName": self.get_name(),
        },
        "fields": self._map_fields(con.fetchall()),
    }
