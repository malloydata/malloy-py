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
"""Test duckdb_connection.py"""

from malloy.data.connection import ConnectionInterface
from malloy.data.duckdb import DuckDbConnection

from pathlib import Path
import pytest


def test_is_connection_interface():
  duckdb = DuckDbConnection()
  assert isinstance(duckdb, ConnectionInterface)


def test_returns_default_name():
  duckdb = DuckDbConnection()
  assert duckdb.get_name() == "duckdb"


def test_returns_custom_name():
  duckdb = DuckDbConnection(name="custom-duckdb")
  assert duckdb.get_name() == "custom-duckdb"


def test_creates_connection_with_search_path():
  duckdb = DuckDbConnection(home_dir=parent_dir())
  conn = duckdb.get_connection()
  assert fetch_setting(conn, "FILE_SEARCH_PATH") == parent_dir_str()


type_test_data = [
    ("varchar_col_1", "string", None, None),
    ("bigint_col_1", "number", "integer", None),
    ("double_col_1", "number", "float", None),
    ("date_col_1", "date", None, None),
    ("timestamp_col_1", "timestamp", None, None),
    ("time_col_1", "string", None, None),
    ("decimal_col_1", "number", "float", None),
    ("boolean_col_1", "boolean", None, None),
    ("integer_col_1", "number", "integer", None),
    ("array_col_1", "struct", "number", True),
    ("struct_col_1", "struct", "number", False),
    ("unsupported_col_1", "unsupported", "uuid", None),
]


@pytest.mark.parametrize(
    "field_name,expected_type,expected_other_type,is_array", type_test_data)
def test_maps_db_types(field_name, expected_type, expected_other_type,
                       is_array):
  duckdb = DuckDbConnection()
  init_test_table(duckdb)

  field = get_field_def(schema=duckdb.get_schema_for_tables(["test_table"]),
                        col=field_name)
  print(field)
  assert field is not None, f"Database column not found: {field_name}"
  assert field["name"] == field_name
  assert field["type"] == expected_type
  if is_array is not None:
    assert field["structRelationship"]["isArray"] == is_array
    assert field["fields"][0]["type"] == expected_other_type
  elif expected_other_type is not None:
    if expected_type == "number":
      assert field["numberType"] == expected_other_type
    else:
      assert field["rawType"] == expected_other_type


# Utility Methods
def parent_dir():
  return Path(__file__).parent


def parent_dir_str():
  return f"{parent_dir()}"


def fetch_setting(conn, setting):
  return conn.execute(f"SELECT current_setting('{setting}')").fetchall()[0][0]


def init_test_table(duckdb: DuckDbConnection):
  conn = duckdb.get_connection()
  conn.execute("""
CREATE TABLE test_table (
    varchar_col_1           VARCHAR,
    bigint_col_1            BIGINT,
    double_col_1            DOUBLE,
    date_col_1              DATE,
    timestamp_col_1         TIMESTAMP,
    time_col_1              TIME,
    decimal_col_1           DECIMAL,
    boolean_col_1           BOOLEAN,
    integer_col_1           INTEGER,
    array_col_1             INTEGER[],
    struct_col_1            STRUCT(a INTEGER, b STRING),
    unsupported_col_1       UUID,
);
    """)


def get_field_def(schema, col):
  for field in schema["schemas"]["duckdb:test_table"]["fields"]:
    if field["name"] == col:
      return field
  return None
