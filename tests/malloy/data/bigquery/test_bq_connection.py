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

from collections import namedtuple
from malloy.data.connection import ConnectionInterface
from malloy.data.bigquery import BigQueryConnection

from pathlib import Path
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
    ('date_col_1', 'DATE', 'date', None),
    ('string_col_1', 'STRING', 'string', None),
    ('integer_col_1', 'INTEGER', 'number', 'integer'),
    ('int64_col_1', 'INT64', 'number', 'integer'),
    ('float_col_1', 'FLOAT', 'number', 'float'),
    ('float64_col_1', 'FLOAT64', 'number', 'float'),
    ('numeric_col_1', 'NUMERIC', 'number', 'float'),
    ('bignumeric_col_1', 'BIGNUMERIC', 'number', 'float'),
    ('timestamp_col_1', 'TIMESTAMP', 'timestamp', None),
    ('boolean_col_1', 'BOOLEAN', 'boolean', None),
    ('bool_col_1', 'BOOL', 'boolean', None),
]


@pytest.mark.parametrize(
    "field_name,field_type,expected_type,expected_num_type", type_test_data)
def test_maps_db_types(field_name, field_type, expected_type,
                       expected_num_type):
    conn = BigQueryConnection()
    field_metadata = namedtuple('metadata', {"name", "field_type"})
    fields = conn._map_fields(
        [field_metadata(name=field_name, field_type=field_type)])

    print(fields)
    assert fields[0] is not None, (
        "Database column not found: {}".format(field_name))
    assert fields[0]['name'] == field_name
    assert fields[0]['type'] == expected_type
    if expected_num_type is not None:
        assert fields[0]['numberType'] == expected_num_type
