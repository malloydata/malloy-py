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

# bq_connection.py

from __future__ import annotations

import logging

from ..connection import ConnectionInterface
from collections.abc import Sequence
from google.cloud import bigquery


class BigQueryConnection(ConnectionInterface):

    def __init__(self, name: str = "bigquery"):
        self._name = name
        self._log = logging.getLogger(__name__)
        self._client_options = None

    def get_name(self) -> str:
        return self._name

    def withOptions(self, options) -> BigQueryConnection:
        self._client_options = options
        return self

    def get_schema_for_tables(self, tables: Sequence[str]):
        schema = {'schemas': {}}
        for table in tables:
            schema['schemas'][table] = self._to_struct_def(
                table,
                bigquery.Client(self._client_options).get_table(table).schema)
        return schema

    def run_query(self, sql: str):
        return bigquery.Client(self._client_options).query(sql)

    def _to_struct_def(self, table, schema):
        return {
            'type': "struct",
            "name": table,
            "dialect": "standardsql",
            "structSource": {
                "type": "table",
                "tablePath": table
            },
            "structRelationship": {
                "type": "basetable",
                "connectionName": "fake"
            },
            "fields": self._map_fields(schema)
        }

    def _map_fields(self, schema):
        fields = []
        for metadata in schema:
            field = {'name': metadata.name}
            if (metadata.field_type in self.TYPE_MAP.keys()):
                field |= self.TYPE_MAP[metadata.field_type]
            else:
                print("Field type not mapped: {}".format(metadata.field_type))
            fields.append(field)

        return fields

    TYPE_MAP = {
        'DATE': {
            'type': 'date'
        },
        'STRING': {
            'type': 'string'
        },
        'INTEGER': {
            'type': 'number',
            'numberType': 'integer'
        },
        'INT64': {
            'type': 'number',
            'numberType': 'integer'
        },
        'FLOAT': {
            'type': 'number',
            'numberType': 'float'
        },
        'FLOAT64': {
            'type': 'number',
            'numberType': 'float'
        },
        'NUMERIC': {
            'type': 'number',
            'numberType': 'float'
        },
        'BIGNUMERIC': {
            'type': 'number',
            'numberType': 'float'
        },
        'TIMESTAMP': {
            'type': 'timestamp'
        },
        'BOOLEAN': {
            'type': 'boolean'
        },
        'BOOL': {
            'type': 'boolean'
        }

        # TODO(https://cloud.google.com/bigquery/docs/reference/rest/v2/tables#tablefieldschema)
        # BYTES
        # DATETIME
        # TIME
        # GEOGRAPHY
    }
