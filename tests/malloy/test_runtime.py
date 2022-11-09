# Copyright 2022 Google LLC
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# test_runtime.py

import asyncio
import pytest
import pytest_asyncio
import logging

from pathlib import Path
from malloy import Runtime
from malloy.service import ServiceManager
from malloy.data.duckdb import DuckDbConnection

pytestmark = pytest.mark.skipif(
    not Path(ServiceManager.service_path()).exists(),
    reason="Could not find: {}".format(ServiceManager.service_path()),
    allow_module_level=True)

logging.basicConfig(level=logging.ERROR)

home_dir = "{}/test_data".format(Path(__file__).parent)
test_file_01 = "{}/test_file_01.malloy".format(home_dir)
fake_file = "{}/not_a_real_file.malloy".format(home_dir)
query_by_state = """
query: airports -> {
                where: state != null
                group_by: state
                aggregate: airport_count
            }"""


@pytest_asyncio.fixture(scope="module")
async def service_manager():
    service_manager = ServiceManager()
    await service_manager.get_service()
    yield service_manager
    service_manager._kill_service()
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
    sql = await rt.get_sql(query=query_by_state)
    assert sql is None
    assert "[Errno 2] No such file or directory: '{}'".format(
        fake_file) in caplog.text


@pytest.mark.asyncio
async def test_returns_sql(service_manager):
    rt = Runtime(service_manager=service_manager)
    rt.add_connection(DuckDbConnection(home_dir=home_dir))
    rt.load_file(test_file_01)
    sql = await rt.get_sql(query=query_by_state)
    assert sql == """
SELECT 
   airports."state" as "state",
   COUNT( 1) as "airport_count"
FROM 'data/airports.parquet' as airports
WHERE airports."state" IS NOT NULL
GROUP BY 1
ORDER BY 2 desc NULLS LAST
""".lstrip()


@pytest.mark.asyncio
async def test_runs_sql(service_manager):
    rt = Runtime(service_manager=service_manager)
    rt.add_connection(DuckDbConnection(home_dir=home_dir))
    rt.load_file(test_file_01)
    data = (await rt.run("duckdb", query=query_by_state)).df()
    print(data)
    assert data['state'][0] == "TX"
    assert data['airport_count'][0] == 1845
    assert data['state'][22] == "NC"
    assert data['airport_count'][22] == 400
