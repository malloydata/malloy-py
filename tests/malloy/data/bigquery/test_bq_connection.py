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

# test_duckdb_connection.py

from collections import namedtuple
from malloy.data.connection import ConnectionInterface
from malloy.data.bigquery import BigQueryConnection

import pytest


def test_is_connection_interface():
  conn = BigQueryConnection()
  assert isinstance(conn, ConnectionInterface)


def test_returns_default_name():
  conn = BigQueryConnection()
  assert conn.get_name() == "bigquery"


def test_returns_custom_name():
  conn = BigQueryConnection(name="custom-bigquery")
  assert conn.get_name() == "custom-bigquery"


type_test_data = [
  # DATE
  ({"name": "date_col_1", "type": "DATE", "mode": "NULLABLE"},
   {"name": "date_col_1", "type": "date"}),
  # STRING
  ({"name": "string_col_1", "type": "STRING", "mode": "NULLABLE"},
   {"name": "string_col_1", "type": "string"}),
  # INTEGER
  ({"name": "integer_col_1", "type": "INTEGER", "mode": "NULLABLE"},
   {"name": "integer_col_1", "type": "number", "numberType": "integer"}),
  # INT64
  ({"name": "int64_col_1", "type": "INT64", "mode": "NULLABLE"},
   {"name": "int64_col_1", "type": "number", "numberType": "integer"}),
  # FLOAT
  ({"name": "float_col_1", "type": "FLOAT", "mode": "NULLABLE"},
   {"name": "float_col_1", "type": "number", "numberType": "float"}),
  # FLOAT64
  ({"name": "float64_col_1", "type": "FLOAT64", "mode": "NULLABLE"},
   {"name": "float64_col_1", "type": "number", "numberType": "float"}),
  # NUMERIC
  ({"name": "numeric_col_1", "type": "NUMERIC", "mode": "NULLABLE"},
   {"name": "numeric_col_1", "type": "number", "numberType": "float"}),
  # BIGNUMERIC
  ({"name": "bignumeric_col_1", "type": "BIGNUMERIC", "mode": "NULLABLE"},
   {"name": "bignumeric_col_1", "type": "number", "numberType": "float"}),
  # TIMESTAMP
  ({"name": "timestamp_col_1", "type": "TIMESTAMP", "mode": "NULLABLE"},
   {"name": "timestamp_col_1", "type": "timestamp"}),
  # BOOLEAN
  ({"name": "boolean_col_1", "type": "BOOLEAN", "mode": "NULLABLE"},
   {"name": "boolean_col_1", "type": "boolean"}),
  # BOOL
  ({"name": "bool_col_1", "type": "BOOL", "mode": "NULLABLE"},
   {"name": "bool_col_1", "type": "boolean"}),
  # JSON
  ({"name": "json_col_1", "type": "JSON", "mode": "NULLABLE"},
   {"name": "json_col_1", "type": "json"}),
  # STRING ARRAY
  ({"name": "string_array_1", "type": "STRING", "mode": "REPEATED"},
    {"name": "string_array_1",
    "type": "struct",
    "dialect": "standardsql",
    "fields": [{"name": "value", "type": "string"}],
    "structRelationship": {"field": "string_array_1",
                            "isArray": True,
                            "type": "nested"},
    "structSource": {"type": "nested"}
    }
  ),
  # RECORD
  ({"name": "record_1", "type": "RECORD", "mode": "NULLABLE", "fields": [
    {"name": "record_integer_1", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "record_string_1", "type": "STRING", "mode": "NULLABLE"}
  ]},
    {"name": "record_1",
    "dialect": "standardsql",
    "fields": [{"name": "record_integer_1",
                "numberType": "integer",
                "type": "number"},
               {"name": "record_string_1", "type": "string"}],
    "structRelationship": {"type": "inline"},
    "structSource": {"type": "inline"},
    "type": "struct"
    }
  )
]

def _make_field_metadata(field):
  field_metadata = namedtuple(
    "metadata", {"name", "field_type", "mode", "fields"}
  )
  return field_metadata(
        name=field["name"],
        field_type=field["type"],
        mode=field["mode"],
        fields=
          (_make_field_metadata(field) for field in field["fields"])
          if "fields" in field else
          None
  )

@pytest.mark.parametrize(
    "field,expected", type_test_data)
def test_maps_db_types(field, expected):
  conn = BigQueryConnection()
  fields = conn._map_schema([_make_field_metadata(field)])

  assert fields[0] is not None, (
      f"Database column not found: {field['name']}")
  assert fields[0] == expected

@pytest.mark.parametrize(
    "field,expected", type_test_data)
def test_maps_sql_block_types(field, expected):
  conn = BigQueryConnection()
  fields = conn._map_sql_block_schema({"fields": [field]})

  assert fields[0] is not None, (
      f"Database column not found: {field['name']}")
  assert fields[0] == expected
