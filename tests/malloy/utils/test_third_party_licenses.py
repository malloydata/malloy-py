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

# test_third_party_licenses.py
"""Test third_party_licenses.py, verifies license output"""

import pytest

from malloy.utils.third_party_licenses import *

PROJECT_URLS = [
    ("Source, https://github.com/duckdb/duckdb/blob/master/tools/pythonpkg",
     "https://github.com/duckdb/duckdb"),
    ("https://github.com/googleapis/python-api-common-protos",
     "https://github.com/googleapis/python-api-common-protos"),
    ("https://github.com/googleapis/proto-plus-python.git",
     "https://github.com/googleapis/proto-plus-python"),
    ("http://github.com/minrk/appnope", "https://github.com/minrk/appnope")
]


@pytest.mark.parametrize("input,expected", PROJECT_URLS)
def test_extract_project_url(input, expected):
  actual = extract_project_url(input)
  assert actual == expected


def test_get_requirements():
  reqs = get_requirements(REQUIREMENTS_FILES)
  assert len(reqs) > 0
  for key in reqs:
    assert reqs[key] is not None
    assert reqs[key][METADATA_VERSION] is not None
    assert reqs[key][METADATA_NAME] is not None


def test_get_requirements_metadata():
  reqs = get_requirements(REQUIREMENTS_FILES)
  reqs = get_requirements_metadata(reqs)

  for key in reqs:
    if len(reqs[key].keys()) < 3:
      print(f'ERROR: Metadata missing for {key}\n{reqs[key]}')
    assert len(reqs[key].keys()) > 2


def test_validate_data():
  reqs = get_requirements(REQUIREMENTS_FILES)
  reqs = get_requirements_metadata(reqs)
  reqs = get_licenses(reqs)
  validate_data(reqs)
