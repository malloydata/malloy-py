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
"""Malloy IPython magics tabbed renderer."""

import random

# Common CSS block.
css = '''
<style>
/* Style the tab */
.tab {
  overflow: hidden;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
}

/* Style the buttons inside the tab */
.tab button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
}

/* Change background color of buttons on hover */
.tab button:hover {
  background-color: #ddd;
}

/* Create an active/current tablink class */
.tab button.active {
  background-color: #ccc;
}

/* Style the tab content */
.tabcontent {
  display: none;
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-top: none;
}
/* Style the close button */
.topright {
  float: right;
  cursor: pointer;
  font-size: 28px;
}

.topright:hover {
  color: red;
}
</style>
'''

# Common JS block.
js_script = '''
<script>
function openTab(evt, tabName, result_set) {
  var i, tabcontent, tablinks, cur_tabset, cur_tablinks;
  cur_tabset = "tabset-" + result_set;
  cur_tablinks = "tablinks-" + result_set;
  tabcontent = document.getElementsByClassName(cur_tabset);
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName(cur_tablinks);
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}
</script>
'''

# Select HTML result tab by default.
def_tab_js = '''
<script>
document.getElementById("defaultOpen-{rand}").click();
</script>
'''

# Tabbed result set.
html_body = '''

<div class="tab">
  <button class="tablinks-{rand}" onclick="openTab(event, 'HTML-{rand}', '{rand}')" id="defaultOpen-{rand}">HTML</button>
  <button class="tablinks-{rand}" onclick="openTab(event, 'SQL-{rand}', '{rand}')">SQL</button>
</div>

<div id="HTML-{rand}" class="tabcontent tabset-{rand}">
  <span onclick="this.parentElement.style.display='none'" class="topright">&times</span>
  {html}
</div>
<div id="SQL-{rand}" class="tabcontent tabset-{rand}">
  <span onclick="this.parentElement.style.display='none'" class="topright">&times</span>
  <pre>{sql}</pre>
</div>

'''


def get_initial_css_js():
  return css + js_script


def render_results_tab(html: str = '', sql: str = ''):
  # Separate each result set with a random id.
  random_id = str(random.randrange(100, 999))
  return html_body.format(rand=random_id, html=html,
                          sql=sql) + def_tab_js.replace('{rand}', random_id)
