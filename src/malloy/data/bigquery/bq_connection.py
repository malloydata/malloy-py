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

# bq_connection.py
"""Module contains a Malloy connection for BigQuery. """

from __future__ import annotations

import logging

from ..connection import ConnectionInterface
from collections.abc import Sequence
from google.cloud import bigquery


class BigQueryConnection(ConnectionInterface):
  """Basic implementation of a Malloy ConnectionInterface for BigQuery. """

  def __init__(self, name: str = "bigquery"):
    self._name = name
    self._log = logging.getLogger(__name__)
    self._client_options = None

  def get_name(self) -> str:
    return self._name

  def with_options(self, options) -> BigQueryConnection:
    self._client_options = options
    return self

  def get_schema_for_tables(self, tables: Sequence[str]):
    schema = {"schemas": {}}
    for table in tables:
      table_only = table[table.find(":") + 1:]
      schema["schemas"][table] = self._to_struct_def(
          table_only,
          bigquery.Client(self._client_options).get_table(table_only).schema)
    return schema

  def run_query(self, sql: str):
    return bigquery.Client(self._client_options).query(sql)

  def get_schema_for_sql_block(self, name, sql):
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = bigquery.Client(self._client_options).query(
        sql, job_config=job_config)
    return {
        "type":
            "struct",
        "name":
            name,
        "dialect":
            "standardsql",
        "structSource": {
            "type": "sql",
            "method": "subquery",
            "sqlBlock": {
                "sql": sql,
            },
        },
        "structRelationship": {
            "type": "basetable",
            "connectionName": self.get_name(),
        },
        # TODO: Fix protected-access when alternative available
        # pylint: disable=protected-access
        "fields":
            self._map_sql_block_schema(query_job._job_statistics()["schema"]),
    }

  def _to_struct_def(self, table, schema):
    return {
        "type": "struct",
        "name": table,
        "dialect": "standardsql",
        "structSource": {
            "type": "table",
            "tablePath": table
        },
        "structRelationship": {
            "type": "basetable",
            "connectionName": "fake"
        },
        "fields": self._map_schema(schema)
    }

  def _to_array_struct_def(self, name):
    return {
        "type": "struct",
        "name": name,
        "dialect": "standardsql",
        "structSource": {
            "type": "nested"
        },
        "structRelationship": {
            "type": "nested",
            "field": name,
            "isArray": True,
        },
    }

  def _to_inner_struct_def(self, name, mode):
    return {
        "type": "struct",
        "dialect": "standardsql",
        "structSource": {
            "type": "nested"
        } if mode == "REPEATED" else {
            "type": "inline"
        },
        "structRelationship": {
            "type": "nested",
            "field": name,
            "isArray": False
        } if mode == "REPEATED" else {
            "type": "inline"
        },
    }

  def _map_schema(self, schema):
    fields = []
    for metadata in schema:
      field = {"name": metadata.name}
      is_struct = metadata.field_type in ["STRUCT", "RECORD"]
      if metadata.mode == "REPEATED" and not is_struct:
        if metadata.field_type in self.TYPE_MAP:
          field |= self._to_array_struct_def(metadata.name)
          malloy_type = {"name": "value"}
          malloy_type |= self.TYPE_MAP[metadata.field_type]
          field["fields"] = [malloy_type]
      elif is_struct:
        field |= self._to_inner_struct_def(metadata.name, metadata.mode)
        field["fields"] = self._map_schema(metadata.fields)
      elif metadata.field_type in self.TYPE_MAP:
        field |= self.TYPE_MAP[metadata.field_type]
      else:
        field["type"] = "unsupported"
        field["rawType"] = metadata.field_type.lower()
      fields.append(field)

    return fields

  def _map_sql_block_schema(self, schema):
    fields = []
    for schema_field in schema["fields"]:
      field = {"name": schema_field["name"]}
      is_struct = schema_field["type"] in ["STRUCT", "RECORD"]
      if schema_field["mode"] == "REPEATED" and not is_struct:
        if schema_field["type"] in self.TYPE_MAP:
          field |= self._to_array_struct_def(schema_field["name"])
          malloy_type = {"name": "value"}
          malloy_type |= self.TYPE_MAP[schema_field["type"]]
          field["fields"] = [malloy_type]
      elif schema_field["type"] in ["STRUCT", "RECORD"]:
        field |= self._to_inner_struct_def(schema_field["name"],
                                           schema_field["mode"])
        field["fields"] = self._map_sql_block_schema(schema_field)
      elif schema_field["type"] in self.TYPE_MAP:
        field |= self.TYPE_MAP[schema_field["type"]]
      else:
        field["type"] = "unsupported"
        field["rawType"] = schema_field["type"].lower()
      fields.append(field)

    return fields

  TYPE_MAP = {
      "DATE": {
          "type": "date"
      },
      "STRING": {
          "type": "string"
      },
      "INTEGER": {
          "type": "number",
          "numberType": "integer"
      },
      "INT64": {
          "type": "number",
          "numberType": "integer"
      },
      "FLOAT": {
          "type": "number",
          "numberType": "float"
      },
      "FLOAT64": {
          "type": "number",
          "numberType": "float"
      },
      "NUMERIC": {
          "type": "number",
          "numberType": "float"
      },
      "BIGNUMERIC": {
          "type": "number",
          "numberType": "float"
      },
      "TIMESTAMP": {
          "type": "timestamp"
      },
      "BOOLEAN": {
          "type": "boolean"
      },
      "BOOL": {
          "type": "boolean"
      },
      "JSON": {
          "type": "json"
      }
      # pylint: disable=line-too-long
      # TODO(https://cloud.google.com/bigquery/docs/reference/rest/v2/tables#tablefieldschema)
      # BYTES
      # DATETIME
      # TIME
      # GEOGRAPHY
  }
