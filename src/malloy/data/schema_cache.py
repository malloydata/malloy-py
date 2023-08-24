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

# schema_cache.py
"""Module for caching schema."""

from collections.abc import Sequence
from malloy.data.connection import ConnectionInterface


class SchemaCache:
  """Basic schema cache. Cache schema per connection."""

  def __init__(self):
    self._schema_cache = {}

  def _cache_schema(self, connection: str, schema: {}):
    for key in schema["schemas"]:
      self._schema_cache.setdefault(connection, {})
      self._schema_cache[connection][key] = schema["schemas"][key]

  def _get_cached_schema(self, connection: str, tables: Sequence[(str, str)]):
    cached_schema = {"schemas": {}}
    uncached_tables = []
    for (key, table) in tables:
      if (connection in self._schema_cache and
          key in self._schema_cache[connection]):
        cached_schema["schemas"][key] = self._schema_cache[connection][key]
      else:
        uncached_tables.append((key, table))
    return [cached_schema, uncached_tables]

  def get_schema_for_tables(self, connection_name: str,
                            connection: ConnectionInterface,
                            tables: Sequence[(str, str)]):
    [cached_schemas,
     uncached_tables] = self._get_cached_schema(connection_name, tables)
    new_schemas = connection.get_schema_for_tables(uncached_tables)
    self._cache_schema(connection_name, new_schemas)
    combined_schemas = {"schemas": {}}
    combined_schemas["schemas"] = {
        **new_schemas["schemas"],
        **cached_schemas["schemas"],
    }
    return combined_schemas
