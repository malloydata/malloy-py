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
from IPython import display
import argparse
import asyncio
import atexit
import malloy
import nest_asyncio
import shlex
from malloy.data.bigquery import BigQueryConnection
from malloy.data.duckdb import DuckDbConnection
from malloy.data.connection_manager import DefaultConnectionManager
from malloy.service import ServiceManager
from malloy import Runtime
from malloy.runtime import MalloyRuntimeError
from .schema_view import render_schema
from .tab_renderer import get_initial_css_js, render_results_tab

nest_asyncio.apply()

DEFAULT_MODEL_VAR = "__malloy_model"


class MalloyArgumentError(Exception):
  """Exception thrown by MalloyMagicArgumentParser when a parsing
  error occurs.
  """
  pass


class MalloyMagicArgumentParser(argparse.ArgumentParser):
  """ArgumentParser sub-class that throws a MalloyArgumentError
  exception instead of calling sys.exit().
  """

  def exit(self, status=0, message=None):
    if message:
      raise MalloyArgumentError(message)


runtime: Runtime = None

# Argument parser for the %%malloy_model magic
model_arg_parser = MalloyMagicArgumentParser(
    prog="%%malloy_model",
    description="Malloy Model cell magic",
    exit_on_error=False)
model_arg_parser.add_argument("modelname", default=DEFAULT_MODEL_VAR, nargs="?")
model_arg_parser.add_argument("-i",
                              "--import",
                              required=False,
                              dest="import_file")

# Argument parser for the %%malloy_query magic
query_arg_parser = MalloyMagicArgumentParser(
    prog="%%malloy_query",
    description="Malloy Query cell magic",
    exit_on_error=False)
query_arg_parser.add_argument("modelname", default=DEFAULT_MODEL_VAR, nargs="?")
query_arg_parser.add_argument("varname", default=None, nargs="?")


def _cleanup_runtime():
  """Tear down runtime when the magic is unloaded or the process exits"""
  if runtime:
    print("Malloy out")
    runtime.shutdown()


atexit.register(_cleanup_runtime)

loop = asyncio.get_event_loop()


async def _malloy_model(line, cell):
  """Dispatch a malloy model cell to the malloy client.

  Args:
    line: Storage location
    cell: Malloy model
  """
  try:
    args = model_arg_parser.parse_args(shlex.split(line))
  except MalloyArgumentError as e:
    print(f"🚫 {e.args[0]}")
    return

  var_name = args.modelname

  if args.import_file:
    runtime.load_file(args.import_file)
  else:
    runtime.load_source("\n" + cell)

  try:
    model = await runtime.compile_model()

    IPython.get_ipython().user_ns[var_name] = runtime
    if model:
      display.display(display.HTML(render_schema(model)))
  except MalloyRuntimeError as e:
    print(f"🚫 {e.args[0]}")
    IPython.get_ipython().user_ns[var_name] = None


def malloy_model(line, cell=None):
  """Dispatch a malloy model cell to the malloy client.

  Args:
    line: Storage location
    cell: Malloy model
  """
  loop.run_until_complete(_malloy_model(line, cell))


async def _malloy_query(line: str, cell: str):
  """Async backend to malloy_query()
  
  Args:
    line: Model name and query storage variable as whitespace
    separated swing
    cell: Malloy query
  """

  try:
    args = query_arg_parser.parse_args(shlex.split(line))
  except MalloyArgumentError as e:
    print(f"🚫 {e.args[0]}")
    return

  model_var = args.modelname
  results_var = args.varname

  if results_var:
    IPython.get_ipython().user_ns[results_var] = None

  if model := IPython.get_ipython().user_ns.get(model_var):
    try:
      render_results = results_var is None
      [job_result, html_content,
       sql] = await model.run(query="\n" + cell, render_results=render_results)
      if job_result is None:
        print("No results")
      elif results_var:
        IPython.get_ipython().user_ns[results_var] = job_result
        print("✅ Stored in", results_var)
      elif html_content:
        tabbed_html = render_results_tab(html_content, sql)
        display.display(display.HTML(tabbed_html))
    except MalloyRuntimeError as e:
      print(f"🚫 {e.args[0]}")
  else:
    print("Please run the cell containing the model")


def malloy_query(line: str, cell: str):
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
  display.display(display.HTML(get_initial_css_js()))

  ipython.register_magic_function(malloy_model, "line_cell")
  ipython.register_magic_function(malloy_query, "cell")


# pylint: disable=unused-argument
def unload_ipython_extension(ipython):
  _cleanup_runtime()
