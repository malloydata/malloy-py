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


class DuckDbException(Exception):
  pass


class DuckDbConnection(ConnectionInterface):
  """Basic implementation of a Malloy ConnectionInterface for DuckDb. """

  _table_regex = re.compile("^duckdb:(.+)$")

  def __init__(self, home_dir=None, name="duckdb"):
    self._log = logging.getLogger(f"{__name__}({name})")
    self._name = name
    self._client_options = {}
    if home_dir is None:
      self._home_directory = None
    else:
      self._home_directory = Path(home_dir).resolve()
    self._con = None
    self._log.debug("DuckDbConnection(\"%s\") initialized", name)

  def get_name(self) -> str:
    return self._name

  def with_options(self, options: dict) -> DuckDbConnection:
    self._client_options = options
    return self

  def with_home_dir(self, path) -> DuckDbConnection:
    self._home_directory = path
    return self

  def get_connection(self):
    if self._con is None:
      self._con = duckdb.connect(database=":memory:",
                                 read_only=False,
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
    """Run a SQL query against this connection"""
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
            "connectionName": self.get_name()
        },
        "fields": self._map_fields(schema)
    }

  def _split_columns(self, schema_string):
    columns = []
    parens = 0
    column = ""
    eat_spaces = True
    for c in schema_string:
      if not eat_spaces or c != " ":
        eat_spaces = False
        if not parens and c == ",":
          columns.append(column)
          column = ""
          eat_spaces = True
        else:
          column += c
        if c == "(":
          parens += 1
        elif c == ")":
          parens -= 1
    columns.append(column)
    return columns

  def _string_to_schema(self, schema_string):
    schema = []
    columns = self._split_columns(schema_string)
    for column in columns:
      column_match = re.match(r"^([^\s]+) (.*)$", column)
      if column_match:
        schema.append([column_match.group(1), column_match.group(2)])
      else:
        raise DuckDbException(
            f"Badly form Structure definition ${schema_string}")
    return schema

  def _map_fields(self, schema):
    fields = []
    for metadata in schema:
      [name, field_type, *_] = metadata
      field = {"name": name}

      # Arrays are <field_type>[]
      array_match = re.match(r"^(.*)\[\]$", field_type)
      is_array = array_match is not None
      if is_array:
        field_type = array_match.group(1)

      # DECIMAL type includes precision ex. DECIMAL(18,3)
      if field_type.startswith("DECIMAL"):
        field_type = "DECIMAL"

      # Structs are STRUCT(field1,field2,...)
      struct_match = re.match(r"^STRUCT\((.*)\)$", field_type)
      is_struct = struct_match is not None

      if is_struct:
        sub_schema = self._string_to_schema(struct_match.group(1))
        inner_struct_def = {
            "type": "struct",
            "name": name,
            "dialect": "duckdb",
            "structSource": {
                "type": "nested" if is_array else "inline"
            },
            "structRelationship": {
                "type": "nested" if is_array else "inline",
                "field": name,
                "isArray": False,
            },
            "fields": self._map_fields(sub_schema),
        }
        fields.append(inner_struct_def)
      else:
        if field_type in self.TYPE_MAP:
          mapped_type = self.TYPE_MAP[field_type]
        else:
          mapped_type = {"type": "unsupported", "rawType": field_type.lower()}
        if is_array:
          inner_struct_def = {
              "type": "struct",
              "name": name,
              "dialect": "duckdb",
              "structSource": {
                  "type": "nested"
              },
              "structRelationship": {
                  "type": "nested",
                  "field": name,
                  "isArray": True,
              },
              "fields": [{
                  "name": "value",
              } | mapped_type],
          }
          fields.append(inner_struct_def)
        else:
          field |= mapped_type
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
      "TINYINT": {
          "type": "number",
          "numberType": "integer"
      },
      "SMALLINT": {
          "type": "number",
          "numberType": "integer"
      },
      "UBIGINT": {
          "type": "number",
          "numberType": "integer"
      },
      "UINTEGER": {
          "type": "number",
          "numberType": "integer"
      },
      "UTINYINT": {
          "type": "number",
          "numberType": "integer"
      },
      "USMALLINT": {
          "type": "number",
          "numberType": "integer"
      },
      "HUGEINT": {
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
