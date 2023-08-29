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
"""Malloy schema renderer styles"""

schema_styles = """
<style>
  body {
    color:  var(--vscode-foreground, inherit);
  }

  ul {
    margin: 5px 0;
    padding: 0 0.75em;
    list-style-type: none;
  }

  li.schema {
    list-style: none;
  }

  .hidden ul {
    display: none;
  }

  li.fields {
    margin: 2px 0;
  }

  li.fields label {
    display: block;
    font-size: 10px;
    margin-left: 5px;
    text-transform: uppercase;
  }

  .explore_name {
    line-height: 2em;
  }

  .field {
    white-space: nowrap;
    display: flex;
    vertical-align: middle;
    border: 1px solid var(--vscode-widget-border, rgba(128, 128, 128, 0.5));
    border-radius: 20px;
    padding: 0.5em 1em;
    margin: 0.25em;
  }

  .field_list {
    display: flex;
    flex-wrap: wrap;
    margin-top: 0.25em;
  }

  .field_name {
    padding-left: 3px;
  }

  .field_name,
  svg,
  span,
  b {
    vertical-align: middle;
    display: inline-block;
  }

  span.closed {
    display: none;
  }

  span.open {
    display: inline-block;
  }

  .hidden span.closed {
    display: inline-block;
  }

  .hidden span.open {
    display: none;
  }
</style>
"""
