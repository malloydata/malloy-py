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

# connection_manager.py

import abc
import logging
from collections.abc import Sequence
from malloy.data.connection import ConnectionInterface

"""Manages a collection of connections required for compiling a malloy model."""
class ConnectionManagerInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_connection')
                and callable(subclass.get_connection)
                and hasattr(subclass, 'add_connection')
                and callable(subclass.add_connection))
    
    @abc.abstractmethod
    def get_connection(self, name: str) -> ConnectionInterface:
        raise NotImplementedError 
    
    @abc.abstractmethod
    def add_connection(self, connection: ConnectionInterface) -> None:
        raise NotImplementedError 

   

"""Default connection manager implementation, a basic mapping of connections to connection name."""
class DefaultConnectionManager(ConnectionManagerInterface):

    def __init__(self):
        self._log = logging.getLogger(__name__)
        self._connections = {}

    def get_connection(self, name: str) -> ConnectionInterface:
        return self._connections[name]

    def add_connection(self, connection: ConnectionInterface) -> None:
        self._log.debug("Adding connection: {}".format(connection.get_name()))
        self._connections[connection.get_name()] = connection
        