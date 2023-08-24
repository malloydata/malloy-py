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

# test_schema_cache.py
"""Test schema_cache.py"""

import logging

from pathlib import Path
from malloy.data.duckdb import DuckDbConnection
from malloy.data.schema_cache import SchemaCache

logging.basicConfig(level=logging.ERROR)

home_dir = f"{Path(__file__).parent.parent}/test_data"
test_file_01 = f"{home_dir}/test_file_01.malloy"
query_by_state = """
query: airports -> {
                where: state != null
                group_by: state
                aggregate: airport_count
            }"""
tables = [("duckdb:data/airports.parquet", "data/airports.parquet")]


def test_saves_schema_to_cache():
  sc = SchemaCache()
  connection = DuckDbConnection(home_dir=home_dir)
  sc.get_schema_for_tables("duckdb", connection, tables)
  # pylint: disable=protected-access
  cache = sc._schema_cache
  assert cache["duckdb"]["duckdb:data/airports.parquet"] is not None


def test_gets_saved_schema():
  sc = SchemaCache()
  connection = DuckDbConnection(home_dir=home_dir)
  sc.get_schema_for_tables("duckdb", connection, tables)
  # pylint: disable=protected-access
  [cache, uncached_tables] = sc._get_cached_schema("duckdb", tables)
  assert cache["schemas"]["duckdb:data/airports.parquet"] is not None
  assert len(uncached_tables) == 0
