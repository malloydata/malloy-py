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
  .malloy_schema {
    color:  var(--vscode-foreground, inherit);
  }

  .malloy_schema ul {
    margin: 5px 0;
    padding: 0 0.75em;
    list-style-type: none;
  }

  .malloy_schema li.schema {
    list-style: none;
  }

  .malloy_schema .hidden ul {
    display: none;
  }

  .malloy_schema li.fields {
    margin: 2px 0;
  }

  .malloy_schema li.fields label {
    display: block;
    font-size: 10px;
    margin-left: 5px;
    margin-top: 0.5em;
    text-transform: uppercase;
  }

  .malloy_schema .explore_name {
    line-height: 2em;
    font-weight: 600;
  }

  .malloy_schema .field {
    white-space: nowrap;
    display: flex;
    vertical-align: middle;
    border: 1px solid var(--vscode-notebook-cellBorderColor, rgba(128, 128, 128, 0.5));
    border-radius: 8px;
    padding: 0.25em 0.75em;
    margin: 0.2em;
  }

  .malloy_schema .field_list {
    display: flex;
    flex-wrap: wrap;
    margin-top: 0.25em;
  }

  .malloy_schema .field_name {
    padding-left: 3px;
  }

  .malloy_schema .field_name,
  .malloy_schema svg,
  .malloy_schema span,
  .malloy_schema b {
    vertical-align: middle;
    display: inline-block;
  }

  .malloy_schema span.closed {
    display: none;
  }

  .malloy_schema span.open {
    display: inline-block;
  }

  .malloy_schema .hidden span.closed {
    display: inline-block;
  }

  .malloy_schema .hidden span.open {
    display: none;
  }
</style>
"""
