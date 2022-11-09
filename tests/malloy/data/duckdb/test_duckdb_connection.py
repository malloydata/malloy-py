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
    duckdb = DuckDbConnection(home_dir=dir())
    conn = duckdb.get_connection()
    assert fetch_setting(conn, 'FILE_SEARCH_PATH') == dir_str()

type_test_data = [
    ('varchar_col_1', 'string', None),
    ('bigint_col_1', 'number', 'integer'),
    ('double_col_1', 'number', 'float'),
    ('date_col_1', 'date', None),     
    ('timestamp_col_1', 'timestamp', None),
    ('time_col_1', 'string', None),   
    ('decimal_col_1', 'number', 'float'),
    ('boolean_col_1', 'boolean', None),
    ('integer_col_1', 'number', 'integer'),
]

@pytest.mark.parametrize("field_name,expected_type,expected_num_type", type_test_data)
def test_maps_db_types(field_name, expected_type, expected_num_type):
    duckdb = DuckDbConnection()
    init_test_table(duckdb)

    field = get_field_def(
        schema=duckdb.get_schema_for_tables(["test_table"]), 
        col=field_name)
    print(field)
    assert field is not None, ("Database column not found: {}".format(field_name))
    assert field['name'] == field_name
    assert field['type'] == expected_type
    if expected_num_type is not None:
        assert field['numberType'] == expected_num_type

# Utility Methods
def dir():
    return Path(__file__).parent

def dir_str():
    return "{}".format(dir())

def fetch_setting(conn, setting):
    return conn.execute("SELECT current_setting('{}')".format(setting)).fetchall()[0][0]

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
);
    """)

def get_field_def(schema, col):
    for field in schema['schemas']['duckdb:test_table']['fields']:
        if field['name'] == col:
            return field
    return None 