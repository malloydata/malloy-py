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
import os

# CSS block.
css = '''
<style>
div.result-outer {
  display: flex;
  flex-direction: column;
  overflow: auto;
  border: 1px solid rgb(65, 65, 65);
  border-radius: 5px;
  margin: 4px 0 12px;
  position: relative;
}

.result-controls-bar {
  display: flex;
  border-bottom: 1px solid rgb(120, 120, 120);;
  justify-content: space-between;
  align-items: center;
  color: #b1b1b1;
}

.result-label {
  font-weight: 500;
  font-size: 12px;
  padding: 0 8px;
}

.result-controls {
  display: flex;
  justify-content: end;
  padding: 5px 5px 0 5px;
  font-size: 12px;
  gap: 3px;
}

.result-controls .result-control {
  border: 0;
  cursor: pointer;
  background-color: inherit;
  padding: 3px 5px;
  color: #b1b1b1;
  font-weight: lighter;
}

.result-controls .result-control:hover {
  border-bottom: 1px solid #4285f4;
  color: #4285f4;
}

.result-controls .result-control.active {
  border-bottom: 1px solid #4285f4;
  color: #4285f4;
  font-weight: 700;
}

.result-inner td {
  line-height: 16px;
}

div.document .result-inner pre {
  border: none;
  background-color: transparent;
  padding: 8px;
  margin: 0;
}

div.document .result-middle[data-result-kind="sql"] pre,
div.document .result-middle[data-result-kind="json"] pre {
  background-color: #fbfbfb;
}

</style>
'''

# JS block.
tabbed_html_js = '''
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

# bundled renderer.
bundled_renderer_js = '''<script>
function renderResults() {{
  var result = JSON.parse(`{result}`);
  var preparedResult = JSON.parse({prepared_result});
  var resultElementId = `{result_div}`
  var resultEle = document.getElementById(resultElementId);
  renderMalloyResults(result, {total_rows}, preparedResult).then(
    function(malloyResEle) {{
      resultEle.appendChild(malloyResEle);
    }}
  );
}};

var script = document.querySelector('#malloy-renderer-js');
if (!script) {{
  script = document.createElement('script');
  script.id = 'malloy-renderer-js';
  script.src = 'https://cdn.jsdelivr.net/npm/@malloydata/render@0.0.118/dist/bundle/bundled_renderer.min.js';
  script.async = false;
  script.addEventListener('load', renderResults);
  document.head.appendChild(script);
}} else {{
  renderResults();
}}

</script>
'''

# Tabbed result set.
html_body = '''

<div class="result-outer">
  <div class="result-controls-bar">
    <span class="result-label">QUERY RESULTS</span>
    <div class="result-controls">
      <button class="result-control tablinks-{rand}" onclick="openTab_{rand}(event, 'HTML-{rand}')" data-result-kind="html" id="defaultOpen-{rand}">HTML</button>
      <button class="result-control tablinks-{rand}" onclick="openTab_{rand}(event, 'JSON-{rand}')" data-result-kind="json">JSON</button>
      <button class="result-control tablinks-{rand}" onclick="openTab_{rand}(event, 'SQL-{rand}')" data-result-kind="sql">SQL</button>
    </div>
  </div>
  <div class="result-middle tabset-{rand}" data-result-kind="html" id="HTML-{rand}">
    <div class="result-inner" id="{result_div}">
    </div>
  </div>
  <div class="result-middle tabset-{rand}" data-result-kind="json" id="JSON-{rand}" >
    <div class="result-inner">
      <pre>{json}</pre>
    </div>
  </div>
  <div class="result-middle tabset-{rand}" data-result-kind="sql" id="SQL-{rand}" >
    <div class="result-inner">
      <pre>{sql}</pre>
    </div>
  </div>
</div>
'''


def render_results_tab(result_json: str, total_rows: int, prepared_result: str,
                       sql: str):
  # Separate each result set with a random id.
  random_id = str(random.randrange(100, 999))

  # Set static id when running under tests
  if os.environ.get("PYTEST_VERSION") is not None:
    random_id = "382"

  result_div = "HTML-" + random_id + "-inner"
  tabbed_html = html_body.format(rand=random_id,
                                 json=result_json,
                                 sql=sql,
                                 result_div=result_div)
  return css + tabbed_html + tabbed_html_js.replace(
      "{rand}", random_id) + bundled_renderer_js.format(
          result=result_json,
          prepared_result=prepared_result,
          result_div=result_div,
          total_rows=total_rows)
