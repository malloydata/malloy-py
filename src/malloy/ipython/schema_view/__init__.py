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

from .scripts import schema_scripts
from .styles import schema_styles
from .icons import get_icon_path


def field_sort(a):
  is_aggregate = a.get("expressionType") == "aggregate"
  return (0 if a["type"] == "turtle" else
          4 if a["type"] == "struct" else 2 if is_aggregate else 1, a["name"])


def render_fields(root):
  html = ""
  fields = root["fields"]
  join_relationship = root.get("structRelationship")
  join_type = None
  if join_relationship:
    join_type = join_relationship.get("type")
  icon_type = join_type if join_type else "struct_base"
  schema_name = root.get("as") or root.get("name")
  html += f"""
<li class="schema hidden" onclick="toggleClass(event, 'hidden');"; return false;">
{get_icon_path(icon_type, False)} <b class="schema_name">{schema_name}</b>
<ul>
"""
  for field in sorted(fields, key=field_sort):
    field_type = field.get("type")
    field_name = field.get("as") or field.get("name")
    if field_type == "struct":
      html += "<ul>"
      html += render_fields(field)
      html += "</ul>"
    else:
      is_aggregate = field.get("expressionType") == "aggregate"
      html += f"""
    <li>
      {get_icon_path(field_type, is_aggregate)}
      <span class="field_name">{field_name}</span>
    </li>
  """
  html += """
</ul>
</li>
"""
  return html


def render_schema(model):
  """Render a model into a schema tree"""
  html = schema_styles + schema_scripts
  html += "<ul>\n"
  for schema_name in model["contents"]:
    schema = model["contents"][schema_name]
    html += render_fields(schema)
  html += "</ul>\n"

  return html
