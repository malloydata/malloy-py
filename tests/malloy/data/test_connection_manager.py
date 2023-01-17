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
