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
"""Malloy IPython magics warning renderer."""

STYLES = """
<style type="text/css">
  .malloy_warnings {
    color:  var(--vscode-foreground, inherit);
    font-size: 10px;
  }

  .malloy_warnings ul {
    margin: 5px 0;
    padding: 0 0.75em;
    list-style-type: none;
  }

  .malloy_warnings li {
    background-color: var(--vscode-inputValidation-warningBackground, inherit);
    border-color: var(--vscode-inputValidation-warningBorder, inherit);
    color: var(--vscode-list-warningForeground, inherit);
    list-style: none;
  }
</style>
"""


def render_warnings(warnings):
  html = "<div class=\"malloy_warnings\"><ul>"
  for warning in warnings:
    line_num = warning["at"]["range"]["start"]["line"] + 1
    html += f"<li>⚠️: {warning['message']} at line {line_num}</li>"
  return STYLES + html + "</ul></div>"
