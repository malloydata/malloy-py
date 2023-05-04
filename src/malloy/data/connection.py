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

# connection.py
"""An object capable of returning data needed for compiling a malloy source."""
import abc
from collections.abc import Sequence


class ConnectionInterface(metaclass=abc.ABCMeta):
  """Basic definition of a Malloy connection interface. """

  @classmethod
  def __subclasshook__(cls, subclass):
    return (hasattr(subclass, "get_schema_for_tables") and
            callable(subclass.get_schema_for_tables) and
            hasattr(subclass, "run_query") and callable(subclass.run_query) and
            hasattr(subclass, "get_name") and callable(subclass.get_name) and
            hasattr(subclass, "get_schema_for_sql_block") and
            callable(subclass.get_schema_for_sql_block))

  @abc.abstractmethod
  def get_name(self, sql: str):
    raise NotImplementedError

  @abc.abstractmethod
  def get_schema_for_tables(self, tables: Sequence[str]):
    raise NotImplementedError

  @abc.abstractmethod
  def get_schema_for_sql_block(self, name: str, sql: str):
    raise NotImplementedError

  @abc.abstractmethod
  def run_query(self, sql: str):
    raise NotImplementedError
