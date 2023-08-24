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

li.field {
  margin: 2px 0;
}

svg,
.field_name,
.schema_name {
  vertical-align: middle;
  display: inline-block;
}
</style>
"""
