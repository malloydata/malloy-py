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

# CSS block.
css = '''
<style>
/* Style the tab */
.tab {
  overflow: auto;
  background-color: inherit;
}

/* Style the buttons inside the tab */
.tab button {
  color: inherit;
  font-weight: lighter;
  background-color: inherit;
  float: right;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 10px 10px;
  transition: 0.1s;
}

/* Change background color of buttons on hover */
.tab button:hover {
  font-weight: 700;
}

/* Create an active/current tablink class */
.tab button.active {
  font-weight: 900;
}

/* Style the tab content */
.tabcontent {
  display: none;
  padding: 6px 12px;
  border: 1px solid #ccc;
  overflow: auto;
}
</style>
'''

# JS block.
js_script = '''
<script>
function openTab_{rand}(evt, tabName) {
  var i, tabcontent, tablinks, cur_tabset, cur_tablinks;
  var shouldClose = false;
  if (evt.currentTarget.classList.contains("active")) {
  	shouldClose = true;
  }
  cur_tabset = "tabset-{rand}";
  cur_tablinks = "tablinks-{rand}";
  tabcontent = document.getElementsByClassName(cur_tabset);
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName(cur_tablinks);
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  if (shouldClose) {
  	evt.currentTarget.className.replace(" active", "");
    event.preventDefault();
  	event.stopPropagation();
  } else {
  	document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }
}

document.getElementById("defaultOpen-{rand}").click();
</script>
'''

# Tabbed result set.
html_body = '''

<div class="tab">
  <button class="tablinks-{rand}" onclick="openTab_{rand}(event, 'SQL-{rand}')">SQL</button>
  <button class="tablinks-{rand}" onclick="openTab_{rand}(event, 'HTML-{rand}')" id="defaultOpen-{rand}">HTML</button>
</div>

<div id="HTML-{rand}" class="tabcontent tabset-{rand}">
  {html}
</div>
<div id="SQL-{rand}" class="tabcontent tabset-{rand}">
  <pre>{sql}</pre>
</div>

'''


def render_results_tab(html: str = '', sql: str = ''):
  # Separate each result set with a random id.
  random_id = str(random.randrange(100, 999))
  return css + html_body.format(rand=random_id, html=html,
                                sql=sql) + js_script.replace(
                                    '{rand}', random_id)
