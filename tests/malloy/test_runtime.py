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

# test_runtime.py
"""Test runtime.py"""

import asyncio
import json
import re
import pytest
import pytest_asyncio

from absl import logging
from pathlib import Path
from malloy import Runtime
from malloy.service import ServiceManager
from malloy.data.duckdb import DuckDbConnection
from malloy.data.snowflake import SnowflakeConnection
from snowflake.connector import Error as SnowflakeError

pytestmark = pytest.mark.skipif(
    not Path(ServiceManager.service_path()).exists(),
    reason=f"Could not find: {ServiceManager.service_path()}",
)

logging.set_verbosity(logging.ERROR)

home_dir = f"{Path(__file__).parent}/test_data"
test_file_01 = f"{home_dir}/test_file_01.malloy"
fake_file = f"{home_dir}/not_a_real_file.malloy"
query_by_state = """
run: airports -> {
                where: state != null
                group_by: state
                aggregate: airport_count
            }"""


@pytest_asyncio.fixture(scope="module", name="service_manager")
async def fixture_service_manager():
  service_manager = ServiceManager()
  await service_manager.get_service()
  yield service_manager
  service_manager.shutdown()
  await asyncio.sleep(0.1)


@pytest.fixture(scope="module")
def event_loop():
  loop = asyncio.get_event_loop_policy().new_event_loop()
  yield loop
  loop.close()


@pytest.mark.asyncio
async def test_logs_error_and_returns_none_if_file_not_found(
    caplog, service_manager):
  rt = Runtime(service_manager=service_manager)
  rt.add_connection(DuckDbConnection(home_dir=home_dir))
  rt.load_file(fake_file)
  [sql, connection] = await rt.compile_malloy(query=query_by_state)
  assert sql is None
  assert connection is None
  assert f"[Errno 2] No such file or directory: '{fake_file}'" in caplog.text


@pytest.mark.asyncio
async def test_returns_sql(service_manager):
  rt = Runtime(service_manager=service_manager)
  rt.add_connection(DuckDbConnection(home_dir=home_dir))
  rt.load_file(test_file_01)
  [sql, connection] = await rt.get_sql(query=query_by_state)
  assert (sql == """
SELECT\x20
   base."state" as "state",
   COUNT(1) as "airport_count"
FROM 'data/airports.parquet' as base
WHERE base."state" IS NOT NULL
GROUP BY 1
ORDER BY 2 desc NULLS LAST
""".lstrip())
  assert connection == "duckdb"


@pytest.mark.asyncio
async def test_runs_sql(service_manager):
  rt = Runtime(service_manager=service_manager)
  rt.add_connection(DuckDbConnection(home_dir=home_dir))
  rt.load_file(test_file_01)
  data = await rt.run(query=query_by_state)
  df_data = data.to_dataframe()
  assert df_data["state"][0] == "TX"
  assert df_data["airport_count"][0] == 1845
  assert df_data["state"][22] == "NC"
  assert df_data["airport_count"][22] == 400


@pytest.mark.asyncio
async def test_with():
  with Runtime() as rt:
    rt.add_connection(DuckDbConnection(home_dir=home_dir))
    rt.load_file(test_file_01)
    data = await rt.run(query=query_by_state)
    df_data = data.to_dataframe()
    assert df_data["state"][0] == "TX"
    assert df_data["airport_count"][0] == 1845
    assert df_data["state"][22] == "NC"
    assert df_data["airport_count"][22] == 400


@pytest.mark.asyncio
async def test_another_with():
  """Verify that service manager can be re-used"""
  with Runtime() as rt:
    rt.add_connection(DuckDbConnection(home_dir=home_dir))
    rt.load_file(test_file_01)
    data = await rt.run(query=query_by_state)
    df_data = data.to_dataframe()
    assert df_data["state"][0] == "TX"
    assert df_data["airport_count"][0] == 1845
    assert df_data["state"][22] == "NC"
    assert df_data["airport_count"][22] == 400


@pytest.mark.asyncio
async def test_returns_prepared_result():
  """verify that prepared result is available"""
  with Runtime() as rt:
    rt.add_connection(DuckDbConnection(home_dir=home_dir))
    rt.load_file(test_file_01)
    [_, _, prepared_result] = await rt.get_sql_and_run(query=query_by_state)
    assert prepared_result is not None and prepared_result != ""


def ensure_snowflake_connectable(conn: SnowflakeConnection):
  try:
    _ = conn.get_connection()
  except SnowflakeError:
    return False
  return True


@pytest.mark.asyncio
async def test_basic_snowflake_malloy_source():
  conn = SnowflakeConnection()
  if not ensure_snowflake_connectable(conn):
    return

  query_by_faa_region = """
run: airports -> {
    where: faa_region != null
    group_by: faa_region
    aggregate: airport_count
}"""
  with Runtime() as rt:
    rt.add_connection(conn)
    test_file_snowflake = f"{home_dir}/test_file_snowflake.malloy"
    rt.load_file(test_file_snowflake)
    data = await rt.run(query=query_by_faa_region)
    df_data = data.to_dataframe()
    assert len(df_data) == 9
    assert df_data["faa_region"][0] == "AGL"
    assert df_data["airport_count"][0] == 4437


@pytest.mark.asyncio
async def test_basic_snowflake_sql_source():
  conn = SnowflakeConnection()
  if not ensure_snowflake_connectable(conn):
    return

  query_by_faa_region = """
run: airports -> {
    where: faa_region != null
    aggregate: airport_count is count()
    group_by: faa_region
}"""
  with Runtime() as rt:
    rt.add_connection(conn)
    rt.load_source(
        "source: airports is snowflake.sql('select * from malloytest.airports')"
    )
    data = await rt.run(query=query_by_faa_region)
    df_data = data.to_dataframe()
    assert len(df_data) == 9
    assert df_data["faa_region"][0] == "AGL"
    assert df_data["airport_count"][0] == 4437
