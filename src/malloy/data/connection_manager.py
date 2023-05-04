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

# connection_manager.py
"""Manages a collection of connections required for compiling a malloy model."""
import abc
import logging
from malloy.data.connection import ConnectionInterface


class ConnectionManagerInterface(metaclass=abc.ABCMeta):
  """Definition of a basic connection manager interface."""

  @classmethod
  def __subclasshook__(cls, subclass):
    return (hasattr(subclass, "get_connection") and
            callable(subclass.get_connection) and
            hasattr(subclass, "add_connection") and
            callable(subclass.add_connection) and
            hasattr(subclass, "get_default_connection_name") and
            callable(subclass.get_default_connection_name))

  @abc.abstractmethod
  def get_connection(self, name: str) -> ConnectionInterface:
    raise NotImplementedError

  @abc.abstractmethod
  def get_default_connection_name(self) -> str:
    raise NotImplementedError

  @abc.abstractmethod
  def add_connection(self, connection: ConnectionInterface) -> None:
    raise NotImplementedError


class DefaultConnectionManager(ConnectionManagerInterface):
  """Default connection manager implementation, a basic mapping of 
      connections to connection name."""

  def __init__(self):
    self._log = logging.getLogger(__name__)
    self._connections = {}

  def get_connection(self, name: str) -> ConnectionInterface:
    if name in self._connections:
      return self._connections.get(name)
    self._log.error("Connection not found: %s", name)

  def get_default_connection_name(self) -> str:
    default_connection = next(iter(self._connections))
    self._log.info("Fetching default connection: %s", default_connection)
    return default_connection

  def add_connection(self, connection: ConnectionInterface) -> None:
    self._log.debug("Adding connection: %s", connection.get_name())
    self._connections[connection.get_name()] = connection
