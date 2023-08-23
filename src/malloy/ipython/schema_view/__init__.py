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
"""Malloy schema renderer"""

from .styles import schema_styles
from .icons import get_icon_path, view_container_icon


def field_sort(a):
  is_aggregate = a.get("expressionType") == "aggregate"
  return (0 if a["type"] == "turtle" else (2 if is_aggregate else 1), a["name"])


def render_schema(model):
  """Render a model into a schema tree"""
  html = schema_styles
  html += """
<h1>Malloy Schema</h1>
"""
  html += "<ul>\n"
  for schema_name in model["contents"]:
    schema = model["contents"][schema_name]
    html += f"""
<li class="schema hidden" onclick="this.classList.toggle('hidden')">
  {view_container_icon} <b class="schema_name">{schema_name}</b>
"""
    html += """
<ul>
"""
    fields = schema["fields"]
    for field in sorted(fields, key=field_sort):
      is_aggregate = field.get("expressionType") == "aggregate"
      html += f"""
<li>
  {get_icon_path(field["type"], is_aggregate)}
  <span class="field_name">{field['name']}</span>
</li>
"""
    html += """
</ul>
"""
    html += """
</li>
"""
  html += """
</ul>
"""

  return html
