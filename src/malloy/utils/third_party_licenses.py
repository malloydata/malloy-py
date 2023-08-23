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

import re
import requests
import sys

from importlib import metadata
from pathlib import Path
from inspect import getsourcefile
from os.path import abspath

REQUIREMENTS_FILES = [
    "requirements.txt", "requirements.dev.txt", "requirements.ipython.txt"
]

THIRD_PARTY_FILENAME = 'third_party.txt'

METADATA_NAME = 'Name'
METADATA_VERSION = 'Version'
METADATA_URL = 'Project URL'
METADATA_LICENSE = 'License'
METADATA_LICENSE_FILE = 'License File'
METADATA_LICENSE_TYPES = 'License Types'

SPECIAL_CASES = {
    'argon2-cffi': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'argon2-cffi-bindings': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'docutils': {
        METADATA_LICENSE_FILE: 'COPYING.txt'
    },
    'duckdb': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'idna': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'pyparsing': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'exceptiongroup': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'grpcio-status': {
        METADATA_URL: 'https://github.com/grpc/grpc.io',
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'grpcio-tools': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'jaraco-classes': {
        METADATA_NAME: 'jaraco.classes'
    },
    'jeepney': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'jupyter-client': {
        METADATA_NAME: 'jupyter_client'
    },
    'jupyter-core': {
        METADATA_NAME: 'jupyter_core'
    },
    'jupyter-events': {
        METADATA_URL: 'https://github.com/jupyter/jupyter_events',
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'jupyter-server': {
        METADATA_NAME: 'jupyter_server'
    },
    'jupyter-server-mathjax': {
        METADATA_URL:
            'https://github.com/jupyter-server/jupyter_server_mathjax',
        METADATA_LICENSE_FILE:
            'LICENSE'
    },
    'jupyter-server-terminals': {
        METADATA_NAME: 'jupyter_server_terminals'
    },
    'more-itertools': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'pep517': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'pexpect': {
        METADATA_URL: 'https://github.com/pexpect/pexpect'
    },
    'pickleshare': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'pytest-notebook': {
        METADATA_NAME: 'pytest_notebook'
    },
    'requests-toolbelt': {
        METADATA_LICENSE_FILE: 'LICENSE',
        METADATA_URL: 'https://github.com/requests/toolbelt'
    },
    'rfc3339-validator': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'rfc3986-validator': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'tomli': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'tinycss2': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'typing-extensions': {
        METADATA_NAME: 'typing_extensions'
    },
    'uri-template': {
        METADATA_URL:
            'https://gitlab.linss.com/open-source/python/uri-template/-',
        METADATA_LICENSE_FILE:
            'LICENSE'
    },
    'webencodings': {
        METADATA_LICENSE_FILE: 'LICENSE'
    },
    'wheel': {
        METADATA_LICENSE_FILE: 'LICENSE.txt'
    }
}


def extract_project_url(input):
  if "http://" in input:
    print(f'WARN: found http, assuming https instead for: {input}')

  match = re.match('^(.+)?(https?:/(/[^/]+)(/[^/]+)(/[^/]+))/?(.+)?$', input)
  if match is None:
    print(f'ERROR: failed to extract project url: {input}')
    return None
  return f'https:/{match.group(3)}{match.group(4)}{match.group(5).removesuffix(".git")}'


def get_requirements(files):
  reqs = {}
  found_error = False
  for file in files:
    lines = open(file, 'r').readlines()
    for line in lines:
      x = re.search('^([^=]+)==(.+)', line)
      if x is None:
        continue
      name = x.group(1).partition('[')[0].lower()
      version = x.group(2)
      if name in reqs.keys() and reqs[name][METADATA_VERSION] != version:
        print(
            f'ERROR: Versions not in sync for: {name}, found {reqs[name][METADATA_VERSION]} and {version}'
        )
        found_error = True
      reqs[name] = {METADATA_NAME: name, METADATA_VERSION: version}

  if found_error:
    raise Exception('Issue trying to get requirements')

  return reqs


def find_license(req):
  license = None
  for path in sys.path:
    path_prefix = f'{path}/{req[METADATA_NAME]}-{req[METADATA_VERSION]}.dist-info'
    test_paths = [
        Path(f'{path_prefix}/licenses/{req.get(METADATA_LICENSE_FILE)}'),
        Path(f'{path_prefix}/{req.get(METADATA_LICENSE_FILE)}'),
        Path(f'{path_prefix}/LICENSE'),
        Path(f'{path_prefix}/LICENSE.txt'),
        Path(f'{path_prefix}/LICENSE.rst'),
        Path(f'{path_prefix}/LICENSE.md'),
    ]
    for test_path in test_paths:
      if test_path.is_file():
        with open(test_path, 'r') as file:
          license = file.read()

  if license is None and req.get(METADATA_URL) is not None and req.get(
      METADATA_LICENSE_FILE) is not None:
    test_urls = [
        f'{req[METADATA_URL]}/raw/main/{req[METADATA_LICENSE_FILE]}',
        f'{req[METADATA_URL]}/raw/master/{req[METADATA_LICENSE_FILE]}'
    ]
    for test_url in test_urls:
      if license is not None:
        break
      request = requests.get(test_url)
      if request.status_code == 200:
        license = request.text

  if license is None:
    print(f'ERROR: License file not found: {req}')

  return license


def get_metadata(req):
  dists = metadata.distributions(path=sys.path)
  license_types = []
  found = False
  for dist in dists:
    # print('dist.metadata["Name"]=' + dist.metadata.get('Name'))
    dist_name = dist.metadata.get('Name')
    if dist_name is None:
      print('Error: name not included in metadata')
      continue

    dist_name = dist_name.lower()
    if dist_name != req[METADATA_NAME]:
      continue

    found = True
    # print(dist.metadata['Name'])

    for classifier in filter(lambda c: c.startswith('License'),
                             dist.metadata.get_all('Classifier', [])):
      req['license_classifier'] = classifier
      license_type = f'{classifier}'.split(' :: ').pop()
      if license_type not in license_types:
        license_types.append(license_type)

    if req.get('license_classifier') is None:
      for license in dist.metadata.get_all('License', []):
        req['license_classifier'] = license

    if req.get(METADATA_LICENSE_FILE) is None:
      for license_file in dist.metadata.get_all('License-File', []):
        req[METADATA_LICENSE_FILE] = license_file

    for project_url in dist.metadata.get_all('Project-URL', []):
      if 'github.com' in project_url and 'sponsors' not in project_url:
        req[METADATA_URL] = extract_project_url(project_url)

    if req.get(METADATA_URL) is None:
      for project_url in dist.metadata.get_all('Home-page', []):
        if 'github.com' in project_url and 'sponsors' not in project_url or 'gitlab.com' in project_url:
          req[METADATA_URL] = extract_project_url(project_url)

    if req.get(METADATA_LICENSE_FILE) is None:
      for license in dist.metadata.get_all('License', []):
        req['license'] = license

    metadata_keys = dist.metadata.keys()
    # print(f'{req[METADATA_NAME]}')
    for key in metadata_keys:
      value = dist.metadata.get(key)

      if 'Classifier' in key and 'License' in value:
        license_type = f'{value}'.split(' :: ').pop()
        if license_type not in license_types:
          license_types.append(license_type)

      if 'License' == key and len(value) < 100 and value not in license_types:
        license_types.append(value)

  if not found:
    print('Error: ' + req[METADATA_NAME] + ' not found')

  req[METADATA_LICENSE_TYPES] = license_types
  return req


def get_requirements_metadata(requirements):
  requirements = apply_special_cases(requirements)

  for key in requirements:
    requirements[key] = get_metadata(requirements[key])

  return requirements


def apply_special_cases(requirements):
  for case in SPECIAL_CASES:

    if requirements.get(case) is None:
      continue

    if SPECIAL_CASES[case].get(METADATA_NAME):
      requirements[case][METADATA_NAME] = SPECIAL_CASES[case][METADATA_NAME]

    if SPECIAL_CASES[case].get(METADATA_LICENSE_FILE):
      requirements[case][METADATA_LICENSE_FILE] = SPECIAL_CASES[case][
          METADATA_LICENSE_FILE]

    if SPECIAL_CASES[case].get(METADATA_URL):
      requirements[case][METADATA_URL] = SPECIAL_CASES[case][METADATA_URL]

  return requirements


def get_licenses(requirements):
  for key in requirements:
    requirements[key][METADATA_LICENSE] = find_license(requirements[key])

  return requirements


def validate_data(requirements):
  issue_found = False
  for key in requirements:
    if requirements[key].get(METADATA_LICENSE) is None:
      issue_found = True
      print(f'ERROR: License not found for {key}\n  {requirements[key]}')

    license_types = requirements[key].get(METADATA_LICENSE_TYPES)
    if license_types is None or len(license_types) < 1:
      issue_found = True
      print(
          f'ERROR: Licence type not classified for {key}\n  {requirements[key]}'
      )

  # if len(requirements[key][METADATA_LICENSE_TYPES]
  #       ) < 1 and requirements[key][METADATA_LICENSE] is not None:
  #   requirements[key][METADATA_LICENSE_TYPES].append(
  #       requirements[key][METADATA_LICENSE].partition('\n')[0])
  #   print(f'{key}: {requirements[key][METADATA_LICENSE_TYPES]}')
  #   print(f'{requirements[key]}')

  if issue_found:
    raise Exception('ERROR: License data validation failed')


def gen_requirements_file(path=f'src/malloy/utils/{THIRD_PARTY_FILENAME}'):
  reqs = get_requirements(REQUIREMENTS_FILES) 
  reqs = get_requirements_metadata(reqs)
  reqs = get_licenses(reqs)
  validate_data(reqs)

  output_file = Path(path)
  with open(output_file, 'w') as file:
    keys = sorted(reqs.keys())
    for key in keys:
      file.write('-------\n')
      file.write(
          f'Package: {reqs[key][METADATA_NAME]}=={reqs[key][METADATA_VERSION]}\n'
      )
      file.write(f'Url: {reqs[key].get(METADATA_URL)}\n')
      file.write(f'License(s): {reqs[key].get(METADATA_LICENSE_TYPES)}\n')
      file.writelines(reqs[key][METADATA_LICENSE])
      file.write('\n')

def output_third_party_licenses():
  script_path = Path(abspath(getsourcefile(lambda:0)))
  license_file_path = Path(script_path.parent, THIRD_PARTY_FILENAME)
  with open(license_file_path, 'r') as file:
    for line in file.readlines():
      print(line)