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
"""Malloy IPython magics"""

import IPython
import asyncio
import atexit
import malloy
import nest_asyncio
from malloy.data.bigquery import BigQueryConnection
from malloy.data.duckdb import DuckDbConnection
from malloy.data.connection_manager import DefaultConnectionManager
from malloy.service import ServiceManager
from duckdb import DuckDBPyConnection

nest_asyncio.apply()

DEFAULT_MODEL_VAR = "model"

runtime = None


def _cleanup_runtime():
  if runtime:
    print("Malloy out")
    runtime.shutdown()


atexit.register(_cleanup_runtime)

loop = asyncio.get_event_loop()


def malloy_model(line, cell):
  """Dispatch a malloy model cell to the malloy client.

  Args:
    line: Storage location
    cell: Malloy model
  """
  var_name = line.strip() or DEFAULT_MODEL_VAR

  model = runtime.load_source(cell)
  IPython.get_ipython().user_ns[var_name] = model
  print("Stored in", var_name)


async def _malloy_query(line, cell):
  """Async backend to malloy_query()"""
  var_names = line.strip().split()
  model_var = var_names[0] or DEFAULT_MODEL_VAR
  results_var = var_names[1] if len(var_names) > 1 else None

  model = IPython.get_ipython().user_ns.get(model_var)
  if model:
    job = await model.run("default_connection", cell)
    if job:
      if isinstance(job, DuckDBPyConnection):
        results = job.fetch_df()
      else:
        results = job.to_dataframe()
      if results_var:
        IPython.get_ipython().user_ns[results_var] = results
        print("Stored in", results_var)
      else:
        return results
    else:
      print("No results")
  else:
    print("Please run the cell containing the model")


def malloy_query(line, cell):
  """Dispatch a malloy query cell to the malloy client.

  Args:
    line: Model name
    cell: Malloy query
  """
  return loop.run_until_complete(_malloy_query(line, cell))


def load_ipython_extension(ipython):
  global runtime
  print("Malloy ahoy")
  user_malloy_service = IPython.get_ipython().user_ns.get("MALLOY_SERVICE")
  service_manager = ServiceManager(user_malloy_service)
  connection_manager = DefaultConnectionManager()
  runtime = malloy.Runtime(connection_manager, service_manager)

  runtime.add_connection(BigQueryConnection())
  runtime.add_connection(DuckDbConnection())

  ipython.register_magic_function(malloy_model, "cell")
  ipython.register_magic_function(malloy_query, "cell")


# pylint: disable=unused-argument
def unload_ipython_extension(ipython):
  _cleanup_runtime()
