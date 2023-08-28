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
b {
 font-size: 12px;
}

ul {
  margin: 5px 0;
  padding: 0 1em;
  list-style-type: none;
}

li.schema {
  list-style: "▼";
  padding-left: 5px;
}

li.schema.hidden {
  list-style: "▶"
}

.hidden ul {
  display: none;
}

li.fields {
  margin: 2px 0;
}

li.fields label {
  text-transform: uppercase;
  font-size: 10px;
  display: block;
  margin-left: 5px;
}

div.field {
  white-space: nowrap;
  display: inline-flex;
  vertical-align: middle;
  border: 1px solid rgba(128, 128, 128, 0.5);
  border-radius: 12px;
  padding: 2px 5px;
  margin: 2px;
}

.field_name {
  padding-left: 3px;
}

svg,
.field_name,
.schema_name {
  vertical-align: middle;
  display: inline-block;
}
</style>
"""
