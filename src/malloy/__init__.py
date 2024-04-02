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

# __init__.py
"""Base module of the Malloy python runtime."""
# Version of the python malloy package
__version__ = "2024.1085"

import importlib

from malloy.runtime import (Runtime)
from malloy.utils.third_party_licenses import (gen_requirements_file,
                                               output_third_party_licenses)
try:
  mod = importlib.import_module("malloy.ipython.ipython_magic")
  load_ipython_extension = getattr(mod, "load_ipython_extension")
  unload_ipython_extension = getattr(mod, "unload_ipython_extension")

except ModuleNotFoundError:
  pass

__all__ = [
    "Runtime", "load_ipython_extension", "unload_ipython_extension",
    "gen_requirements_file", "output_third_party_licenses"
]
