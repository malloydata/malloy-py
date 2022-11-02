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

# test_connection_manager.py

from malloy.data.connection import ConnectionInterface
from malloy.data.connection_manager import ConnectionManagerInterface, DefaultConnectionManager

class FakeConnection(ConnectionInterface):
    def __init__(self, name="Test-Connection"):
        self._name = name
    def get_name(self):
        return self._name
    def get_schema_for_tables(self, tables):
        pass
    def run_query(self, sql):
        pass

def test_default_connection_manager_is_connection_manager():
    manager = DefaultConnectionManager()
    assert isinstance(manager, ConnectionManagerInterface)

def test_adding_connection():
    manager = DefaultConnectionManager()
    connection = FakeConnection()
    manager.add_connection(connection)
    assert manager.get_connection(connection.get_name()) == connection

def test_get_connection_by_name():
    manager = DefaultConnectionManager()
    connection1 = FakeConnection(name="Connection-1")
    connection2 = FakeConnection(name="Connection-2")
    connection3 = FakeConnection(name="Connection-3")
    manager.add_connection(connection1)
    manager.add_connection(connection2)
    manager.add_connection(connection3)
    assert manager.get_connection("Connection-1") == connection1
    assert manager.get_connection("Connection-2") == connection2
    assert manager.get_connection("Connection-3") == connection3