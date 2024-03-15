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

# test_snowflake_connection.py
"""Test snowflake_connection.py"""

from io import StringIO

import pandas
from pandas.testing import assert_frame_equal

from malloy.data.connection import ConnectionInterface
from malloy.data.snowflake import SnowflakeConnection


def test_is_connection_interface():
  conn = SnowflakeConnection()
  assert isinstance(conn, ConnectionInterface)


def test_returns_default_name():
  conn = SnowflakeConnection()
  assert conn.get_name() == "snowflake"


def test_returns_custom_name():
  conn = SnowflakeConnection(name="custom-snowflake")
  assert conn.get_name() == "custom-snowflake"


TEST_QUERY_1 = {
    "sql":
        'SELECT "id", "code" FROM malloytest.airports ORDER BY "id" LIMIT 5',
    "dataframe":
        pandas.read_json(
            StringIO("""
{
  "id": {
    "0": 1,
    "1": 2,
    "2": 3,
    "3": 4,
    "4": 5
  },
  "code": {
    "0": "ADK",
    "1": "AKK",
    "2": "Z13",
    "3": "KKI",
    "4": "AKI"
  }
}
"""),
            dtype={
                "id": "int16",
                "code": "object",
            },
        ),
}


def test_runs_query():
  conn = SnowflakeConnection()
  data = conn.run_query(TEST_QUERY_1["sql"])
  df_data = data.to_dataframe()
  df_data.columns = df_data.columns.str.lower()
  print(df_data)
  assert_frame_equal(df_data, TEST_QUERY_1["dataframe"])
