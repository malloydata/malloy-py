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

# connection.py

import abc
from collections.abc import Sequence

"""An object capable of returning data needed for compiling a malloy source."""
class ConnectionInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_schema_for_tables')
                and callable(subclass.get_schema_for_tables)
                and hasattr(subclass, 'run_query')
                and callable(subclass.run_query)
                and hasattr(subclass, 'get_name')
                and callable(subclass.get_name))
    
    @abc.abstractmethod
    def get_name(self, sql: str):
        raise NotImplementedError 

    @abc.abstractmethod
    def get_schema_for_tables(self, tables: Sequence[str]):
        raise NotImplementedError

    @abc.abstractmethod
    def run_query(self, sql: str):
        raise NotImplementedError
