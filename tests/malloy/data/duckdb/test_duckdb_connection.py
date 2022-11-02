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

# test_duckdb_connection.py

from malloy.data.connection import ConnectionInterface
from malloy.data.duckdb import DuckDbConnection

from pathlib import Path

def test_is_connection_interface():
    duckdb = DuckDbConnection()
    assert isinstance(duckdb, ConnectionInterface)

def test_returns_default_name():
    duckdb = DuckDbConnection()
    assert duckdb.get_name() == "duckdb"

def test_returns_custom_name():
    duckdb = DuckDbConnection(name="custom-duckdb")
    assert duckdb.get_name() == "custom-duckdb"

def  test_creates_connection_with_search_path():
    duckdb = DuckDbConnection(home_dir=dir())
    conn = duckdb.get_connection()
    assert fetch_setting(conn, 'FILE_SEARCH_PATH') == dir_str()

# Utility Methods
def dir():
    return Path(__file__).parent

def dir_str():
    return "{}".format(dir())

def fetch_setting(conn, setting):
    return conn.execute("SELECT current_setting('{}')".format(setting)).fetchall()[0][0]