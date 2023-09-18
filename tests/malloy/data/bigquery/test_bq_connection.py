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

# test_bq_connection.py
"""Test bq_connection.py"""

from collections import namedtuple
from google.cloud import bigquery
from pandas.testing import assert_frame_equal
from malloy.data.connection import ConnectionInterface
from malloy.data.bigquery import BigQueryConnection

from io import StringIO

import pytest
import pandas


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
    ({
        "name": "date_col_1",
        "type": "DATE",
        "mode": "NULLABLE"
    }, {
        "name": "date_col_1",
        "type": "date"
    }),
    # STRING
    ({
        "name": "string_col_1",
        "type": "STRING",
        "mode": "NULLABLE"
    }, {
        "name": "string_col_1",
        "type": "string"
    }),
    # INTEGER
    ({
        "name": "integer_col_1",
        "type": "INTEGER",
        "mode": "NULLABLE"
    }, {
        "name": "integer_col_1",
        "type": "number",
        "numberType": "integer"
    }),
    # INT64
    ({
        "name": "int64_col_1",
        "type": "INT64",
        "mode": "NULLABLE"
    }, {
        "name": "int64_col_1",
        "type": "number",
        "numberType": "integer"
    }),
    # FLOAT
    ({
        "name": "float_col_1",
        "type": "FLOAT",
        "mode": "NULLABLE"
    }, {
        "name": "float_col_1",
        "type": "number",
        "numberType": "float"
    }),
    # FLOAT64
    ({
        "name": "float64_col_1",
        "type": "FLOAT64",
        "mode": "NULLABLE"
    }, {
        "name": "float64_col_1",
        "type": "number",
        "numberType": "float"
    }),
    # NUMERIC
    ({
        "name": "numeric_col_1",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    }, {
        "name": "numeric_col_1",
        "type": "number",
        "numberType": "float"
    }),
    # BIGNUMERIC
    ({
        "name": "bignumeric_col_1",
        "type": "BIGNUMERIC",
        "mode": "NULLABLE"
    }, {
        "name": "bignumeric_col_1",
        "type": "number",
        "numberType": "float"
    }),
    # TIMESTAMP
    ({
        "name": "timestamp_col_1",
        "type": "TIMESTAMP",
        "mode": "NULLABLE"
    }, {
        "name": "timestamp_col_1",
        "type": "timestamp"
    }),
    # BOOLEAN
    ({
        "name": "boolean_col_1",
        "type": "BOOLEAN",
        "mode": "NULLABLE"
    }, {
        "name": "boolean_col_1",
        "type": "boolean"
    }),
    # BOOL
    ({
        "name": "bool_col_1",
        "type": "BOOL",
        "mode": "NULLABLE"
    }, {
        "name": "bool_col_1",
        "type": "boolean"
    }),
    # JSON
    ({
        "name": "json_col_1",
        "type": "JSON",
        "mode": "NULLABLE"
    }, {
        "name": "json_col_1",
        "type": "json"
    }),
    # STRING ARRAY
    ({
        "name": "string_array_1",
        "type": "STRING",
        "mode": "REPEATED"
    }, {
        "name": "string_array_1",
        "type": "struct",
        "dialect": "standardsql",
        "fields": [{
            "name": "value",
            "type": "string"
        }],
        "structRelationship": {
            "field": "string_array_1",
            "isArray": True,
            "type": "nested"
        },
        "structSource": {
            "type": "nested"
        }
    }),
    # RECORD
    ({
        "name":
            "record_1",
        "type":
            "RECORD",
        "mode":
            "NULLABLE",
        "fields": [{
            "name": "record_integer_1",
            "type": "INTEGER",
            "mode": "NULLABLE"
        }, {
            "name": "record_string_1",
            "type": "STRING",
            "mode": "NULLABLE"
        }]
    }, {
        "name": "record_1",
        "dialect": "standardsql",
        "fields": [{
            "name": "record_integer_1",
            "numberType": "integer",
            "type": "number"
        }, {
            "name": "record_string_1",
            "type": "string"
        }],
        "structRelationship": {
            "type": "inline"
        },
        "structSource": {
            "type": "inline"
        },
        "type": "struct"
    })
]


def _make_field_metadata(field):
  field_metadata = namedtuple("metadata",
                              {"name", "field_type", "mode", "fields"})
  return field_metadata(
      name=field["name"],
      field_type=field["type"],
      mode=field["mode"],
      fields=(_make_field_metadata(field) for field in field["fields"])
      if "fields" in field else None)


@pytest.mark.parametrize("field,expected", type_test_data)
def test_maps_db_types(field, expected):
  conn = BigQueryConnection()
  # pylint: disable=protected-access
  fields = conn._map_schema([_make_field_metadata(field)])

  assert fields[0] is not None, (f"Database column not found: {field['name']}")
  assert fields[0] == expected


@pytest.mark.parametrize("field,expected", type_test_data)
def test_maps_sql_block_types(field, expected):
  conn = BigQueryConnection()
  # pylint: disable=protected-access
  fields = conn._map_sql_block_schema({"fields": [field]})

  assert fields[0] is not None, (f"Database column not found: {field['name']}")
  assert fields[0] == expected


def bq_table(table):
  try:
    client = bigquery.Client()
    return client.get_table(table)
  # pylint: disable-next=bare-except
  except:
    return None


def test_runs_query():
  if bq_table("malloy-data.faa.airports") is None:
    pytest.skip()

  conn = BigQueryConnection()

  data = conn.run_query(TEST_QUERY_1["sql"])
  df_data = data.to_dataframe()

  assert_frame_equal(df_data, TEST_QUERY_1["dataframe"])


TEST_QUERY_1 = {
    "sql":
        "SELECT * FROM malloy-data.faa.airports ORDER BY id LIMIT 5;",
    "dataframe":
        pandas.read_json(StringIO("""
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
  },
  "site_number": {
    "0": "50009.*A",
    "1": "50016.1*A",
    "2": "50017.*A",
    "3": "50017.1*C",
    "4": "50020.*A"
  },
  "fac_type": {
    "0": "AIRPORT",
    "1": "AIRPORT",
    "2": "AIRPORT",
    "3": "SEAPLANE BASE",
    "4": "AIRPORT"
  },
  "fac_use": {
    "0": "PU",
    "1": "PU",
    "2": "PU",
    "3": "PU",
    "4": "PU"
  },
  "faa_region": {
    "0": "AAL",
    "1": "AAL",
    "2": "AAL",
    "3": "AAL",
    "4": "AAL"
  },
  "faa_dist": {
    "0": "NONE",
    "1": "NONE",
    "2": "NONE",
    "3": "NONE",
    "4": "NONE"
  },
  "city": {
    "0": "ADAK ISLAND",
    "1": "AKHIOK",
    "2": "AKIACHAK",
    "3": "AKIACHAK",
    "4": "AKIAK"
  },
  "county": {
    "0": "ALEUTIAN ISLANDS",
    "1": "KODIAK",
    "2": "BETHEL",
    "3": "BETHEL",
    "4": "BETHEL"
  },
  "state": {
    "0": "AK",
    "1": "AK",
    "2": "AK",
    "3": "AK",
    "4": "AK"
  },
  "full_name": {
    "0": "ADAK",
    "1": "AKHIOK",
    "2": "AKIACHAK",
    "3": "AKIACHAK",
    "4": "AKIAK"
  },
  "own_type": {
    "0": "MN",
    "1": "PU",
    "2": "PU",
    "3": "PU",
    "4": "PU"
  },
  "longitude": {
    "0": -176.64,
    "1": -154.18,
    "2": -161.42,
    "3": -161.43,
    "4": -161.22
  },
  "latitude": {
    "0": 51.87,
    "1": 56.93,
    "2": 60.9,
    "3": 60.9,
    "4": 60.9
  },
  "elevation": {
    "0": 18,
    "1": 44,
    "2": 25,
    "3": 18,
    "4": 22
  },
  "aero_cht": {
    "0": "W ALEUTIAN ISLS",
    "1": "KODIAK",
    "2": "MC GRATH",
    "3": "MC GRATH",
    "4": "MC GRATH"
  },
  "cbd_dist": {
    "0": 0,
    "1": 1,
    "2": 0,
    "3": 0,
    "4": 0
  },
  "cbd_dir": {
    "0": "W",
    "1": "SW",
    "2": "SE",
    "3": "S",
    "4": "SW"
  },
  "act_date": {
    "0": null,
    "1": null,
    "2": null,
    "3": null,
    "4": null
  },
  "cert": {
    "0": "BS 05/1973",
    "1": null,
    "2": null,
    "3": null,
    "4": null
  },
  "fed_agree": {
    "0": null,
    "1": "NGY",
    "2": "N",
    "3": null,
    "4": "N1"
  },
  "cust_intl": {
    "0": "N",
    "1": "N",
    "2": "N",
    "3": "N",
    "4": "N"
  },
  "c_ldg_rts": {
    "0": "N",
    "1": "N",
    "2": "N",
    "3": "N",
    "4": "N"
  },
  "joint_use": {
    "0": "N",
    "1": null,
    "2": "N",
    "3": "N",
    "4": "N"
  },
  "mil_rts": {
    "0": "Y",
    "1": "Y",
    "2": "Y",
    "3": "N",
    "4": "Y"
  },
  "cntl_twr": {
    "0": "N",
    "1": "N",
    "2": "N",
    "3": "N",
    "4": "N"
  },
  "major": {
    "0": "Y",
    "1": "N",
    "2": "N",
    "3": "N",
    "4": "N"
  }
}
"""),
                         dtype={
                             "id": "Int64",
                             "elevation": "Int64",
                             "cbd_dist": "Int64",
                             "act_date": "object"
                         })
}
