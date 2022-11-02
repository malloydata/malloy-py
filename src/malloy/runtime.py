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

# runtime.py

from __future__ import annotations

import logging
from malloy.data.connection import ConnectionInterface
from malloy.data.connection_manager import ConnectionManagerInterface, DefaultConnectionManager

class Runtime():
    """Malloy runtime class for loading, compiling, and running .malloy files"""

    def __init__(self, connection_manager: ConnectionManagerInterface=DefaultConnectionManager()):
        self._log = logging.getLogger(__name__)
        self._connection_manager = connection_manager
        self._log.debug("Runtime initialized")

    """Add connection to use when referenced by malloy source files."""
    def add_connection(self, connection: ConnectionInterface) -> Runtime:
        self._connection_manager.add_connection(connection)
        return self
