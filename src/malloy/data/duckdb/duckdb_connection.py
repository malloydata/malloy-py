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

# duckdb_connection.py

from __future__ import annotations

from ..connection import ConnectionInterface
from collections.abc import Sequence
from pathlib import Path
import duckdb
import logging
import re

class DuckDbConnection(ConnectionInterface):
    _table_regex = re.compile('^duckdb:(.+)$')

    def __init__(self, home_dir=None, name="duckdb"):
        self._log = logging.getLogger(__name__)
        self._name = name
        self._client_options = None
        if home_dir is None:
            self._home_directory = None
        else:
            self._home_directory = Path(home_dir).resolve()
        self._con = None
        self._log.debug("DuckDbConnection('{}') initialized".format(name))


    def get_name(self) -> str:
        return self._name

    def withOptions(self, options) -> DuckDbConnection:
        self._client_options = options
        return self

    def withHomeDirectory(self, path) -> DuckDbConnection:
        self._home_directory = path
        return self

    def get_connection(self):
        if self._con is None:
            self._con = duckdb.connect(database=':memory:',
                                       config=self._client_options)
            if self._home_directory:
                sql = "SET FILE_SEARCH_PATH='{}'".format(self._home_directory)
                self._log.debug(sql)
                self._con.execute(sql)
        return self._con

    def get_schema_for_tables(self, tables: Sequence[str]):
        self._log.debug("Fetching schema for tables...")
        schema = {'schemas': {}}
        con = self.get_connection()
        for table in tables:
            self._log.debug("Fetching {}".format(table))
            table_def = self._table_regex.match(table).group(1)
            con.execute('DESCRIBE SELECT * FROM \'{}\''.format(table_def))
            schema['schemas'][table] = self._to_struct_def(
                table, con.fetchall())
        return schema

    def run_query(self, sql: str):
        self._log.debug("Running Query:")
        self._log.debug(sql)
        con = self.get_connection()
        con.execute(sql)
        return con

    def _to_struct_def(self, table, schema):
        return {
            'type': "struct",
            "name": table,
            "dialect": "duckdb",
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
            field = {'name': metadata[0]}
            if (metadata[1] in self.TYPE_MAP.keys()):
                field |= self.TYPE_MAP[metadata[1]]
            else:
                self._log.warn("Field type not mapped: {}".format(
                    metadata[1]))
            fields.append(field)

        return fields

    TYPE_MAP = {
        'VARCHAR': {
            'type': 'string'
        },
        'BIGINT': {
            'type': 'number'
        },
        'DOUBLE': {
            'type': 'number'
        },
        'DATE': {
            'type': 'date'
        },
        'TIMESTAMP': {
            'type': 'timestamp'
        },
        'TIME': {
            'type': 'string'
        },
        'DECIMAL': {
            'type': 'number'
        },
        'BOOLEAN': {
            'type': 'boolean'
        },
        'INTEGER': {
            'type': 'number'
        },
    }
