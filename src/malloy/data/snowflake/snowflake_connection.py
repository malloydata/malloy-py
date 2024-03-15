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
"""Module contains a Malloy connection for Snowflake. """

from __future__ import annotations
import hashlib

import logging
from collections.abc import Sequence
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import snowflake.connector as snowflake

from malloy.data.query_results import QueryResultsInterface

from ..connection import ConnectionInterface


class EncloseResultRows(QueryResultsInterface):

  def __init__(self, df: pd.DataFrame):
    self.df = df

  def to_dataframe(self):
    return self.df


# Snowflake types mapped to Malloy types
TYPE_MAP: Dict[str, Dict[str, str]] = {
    # strings
    "varchar": {
        "type": "string"
    },
    "text": {
        "type": "string"
    },
    "string": {
        "type": "string"
    },
    "char": {
        "type": "string"
    },
    "character": {
        "type": "string"
    },
    # integer numbers
    "number": {
        "type": "number",
        "numberType": "integer"
    },
    "numeric": {
        "type": "number",
        "numberType": "integer"
    },
    "dec": {
        "type": "number",
        "numberType": "integer"
    },
    "decimal": {
        "type": "number",
        "numberType": "integer"
    },
    "integer": {
        "type": "number",
        "numberType": "integer"
    },
    "int": {
        "type": "number",
        "numberType": "integer"
    },
    "bigint": {
        "type": "number",
        "numberType": "integer"
    },
    "smallint": {
        "type": "number",
        "numberType": "integer"
    },
    "tinyint": {
        "type": "number",
        "numberType": "integer"
    },
    "byteint": {
        "type": "number",
        "numberType": "integer"
    },
    # floating point numbers
    "float": {
        "type": "number",
        "numberType": "float"
    },
    "float4": {
        "type": "number",
        "numberType": "float"
    },
    "float8": {
        "type": "number",
        "numberType": "float"
    },
    "double": {
        "type": "number",
        "numberType": "float"
    },
    "double precision": {
        "type": "number",
        "numberType": "float"
    },
    "real": {
        "type": "number",
        "numberType": "float"
    },
    "boolean": {
        "type": "boolean"
    },
    # time and date
    "date": {
        "type": "date"
    },
    "timestamp": {
        "type": "timestamp"
    },
    "timestampltz": {
        "type": "timestamp"
    },
    "timestamp_ltz": {
        "type": "timestamp"
    },
    "timestamp with local time zone": {
        "type": "timestamp"
    },
    "timestampntz": {
        "type": "timestamp"
    },
    "timestamp_ntz": {
        "type": "timestamp"
    },
    "timestamp without time zone": {
        "type": "timestamp"
    },
}


def map_field_types(schema: pd.DataFrame) -> List[Dict[str, Any]]:
  fields = []
  for col_name, field_type in zip(schema["column_name"], schema["data_type"]):
    field_type = field_type.lower()
    # DECIMAL type includes precision ex. DECIMAL(38, 0)
    if field_type.startswith("decimal"):
      field_type = "decimal"

    field = {"name": col_name}
    # TODO: add support for variant, object and array types similar to ts
    mapped_type = TYPE_MAP.get(field_type, {
        "type": "unsupported",
        "rawType": field_type
    })
    field |= mapped_type
    fields.append(field)
  return fields


class SnowflakeConnection(ConnectionInterface):
  """Basic implementation of a Malloy ConnectionInterface for Snowflake."""

  def __init__(self, name: str = "snowflake"):
    self._log = logging.getLogger(__name__)
    self._name = name
    self._client_options: Dict[str, Any] = {}
    self._conn: Optional[snowflake.SnowflakeConnection] = None

  def with_options(self, options: Dict[str, Any]) -> SnowflakeConnection:
    self._client_options = options
    return self

  def get_name(self) -> str:
    return self._name

  def get_connection(self) -> snowflake.SnowflakeConnection:
    if self._conn is None:
      self._conn = snowflake.connect(**self._client_options)
    return self._conn

  def _get_schema_df(
      self, tables: Sequence[Tuple[str, str]]) -> Dict[str, pd.DataFrame]:
    schema_dfs: Dict[str, pd.DataFrame] = {}
    for key, table_name in tables:
      query = f"""
SELECT column_name AS "column_name",
       data_type   AS "data_type"
FROM   information_schema.columns
WHERE  table_name = '{table_name}'
OR concat(table_schema, '.', table_name) = '{table_name}'
"""
      schema_dfs[key] = self.run_query(query).to_dataframe()
    return schema_dfs

  def get_schema_for_sql_block(self, name: str, sql: str):

    def to_struct_def(name: str, schema: pd.DataFrame):
      return {
          "type": "struct",
          "name": name,
          "dialect": "snowflake",
          "structSource": {
              "type": "sql",
              "method": "subquery",
              "sqlBlock": {
                  "name": name,
                  "sql": sql,
              },
          },
          "structRelationship": {
              "type": "basetable",
              "connectionName": self.get_name(),
          },
          "fields": map_field_types(schema),
      }

    hash_str = hashlib.md5(sql.encode()).hexdigest()
    temp_table_name = f"tt_{hash_str}"
    self._run_query(f"""
CREATE OR REPLACE TEMP TABLE "{temp_table_name}"
AS
  SELECT *
  FROM ({sql}) AS x
  WHERE FALSE;
""",
                    need_data=False)

    schema_dfs = self._get_schema_df([(temp_table_name, temp_table_name)])
    self._log.debug("Schemas: %s", schema_dfs[temp_table_name].to_string())
    return to_struct_def(temp_table_name, schema_dfs[temp_table_name])

  def get_schema_for_tables(self, tables: Sequence[Tuple[str, str]]):

    def to_struct_def(name: str, schema: pd.DataFrame):
      return {
          "type": "struct",
          "name": name,
          "dialect": "snowflake",
          "structSource": {
              "type": "table",
              "tablePath": name
          },
          "structRelationship": {
              "type": "basetable",
              "connectionName": self.get_name(),
          },
          "fields": map_field_types(schema),
      }

    self._log.debug("Fetching schema for tables: %s", tables)
    schema: Dict[str, Any] = {"schemas": {}}
    schema_dfs = self._get_schema_df(tables)
    for key, table_name in tables:
      schema["schemas"][key] = to_struct_def(table_name, schema_dfs[key])
    return schema

  def _run_query(self,
                 sql: str,
                 need_data=True) -> Optional[QueryResultsInterface]:
    """
    Runs a query against the connection.
    For some queries we do not care about the resulting data. ex: DML queries.
    We should pass need_data = False for such queries.
    """
    self._log.debug("Running query: %s", sql)
    conn = self.get_connection()
    with conn.cursor() as session:
      cursor = session.execute(
          "ALTER SESSION SET QUOTED_IDENTIFIERS_IGNORE_CASE = FALSE;")
      result = cursor.execute(sql)
      if result and need_data:
        return EncloseResultRows(result.fetch_pandas_all())
    return None

  def run_query(self, sql: str) -> QueryResultsInterface:
    """Runs a query against the connection"""
    return self._run_query(sql) or EncloseResultRows(pd.DataFrame())
