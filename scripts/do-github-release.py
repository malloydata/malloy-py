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

import os
import requests

from absl import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging

GITHUB_API_URL = 'https://api.github.com/repos'
GITHUB_API_MIME_TYPE = 'application/vnd.github+json'

GITHUB_UPLOAD_URL = 'https://uploads.github.com/repos'

REPO = 'malloy-py'
REPO_OWNER = 'malloydata'


def create_release(assets):
  [version, tag] = get_version(assets)
  log.info(f'Creating Github Release for {REPO_OWNER}/{REPO}')
  log.info(f'  release type: {tag}')
  log.info(f'  version: {version}')

  response = requests.post(f'{GITHUB_API_URL}/{REPO_OWNER}/{REPO}/releases',
                           headers=get_request_headers(),
                           json={
                               'repo': REPO,
                               'owner': REPO_OWNER,
                               'tag_name': version,
                               'target_commitish': 'main',
                               'name': version,
                               'draft': False,
                               'prerelease': tag != 'final',
                               'generate_release_notes': True,
                           })

  if response.status_code != 201:
    fatal_error(
        f'Request failed:\n [{response.status_code}] - {response.reason}')

  return response.json()


def upload_assets(assets, release):
  log.info('  uploading assets:')
  for asset in assets:
    upload_asset(asset, release)


def upload_asset(asset: Path, release):
  asset_name = str(asset).split("/").pop()
  log.info(f'    uploading: {asset_name}')

  upload_url = f'{GITHUB_UPLOAD_URL}/{REPO_OWNER}/{REPO}/releases/{release.get("id")}/assets?name={asset_name}'

  response = requests.post(
      upload_url,
      headers=get_request_headers(size=asset.stat().st_size),
      data=asset.read_bytes())

  if response.status_code != 201:
    fatal_error(
        f'Request failed:\n [{response.status_code}] - {response.reason}')

  return response.json()


def get_dist_path():
  return Path(Path(__file__).parent, '../dist').resolve()


def get_version(assets):
  for asset in assets:
    asset_str = str(asset)
    if '.tar.gz' in asset_str:
      parts = asset_str.split('.')
      version = f'{parts[0].split("/").pop()}'
      for part in parts[1:]:
        if part == 'tar':
          break
        version = f'{version}.{part}'
      tag = 'final'
      if 'dev' in parts[2]:
        tag = 'dev'
      return [version, tag]

  fatal_error('Failed to parse version from assets')


def get_assets():
  assets = []
  path = get_dist_path()
  log.info(f'  package directory: {path}')
  for item in path.glob('malloy-*'):
    if item.is_file():
      log.info(f'  found asset: {item}')
      assets.append(item)
  return assets


def get_request_headers(size=0):
  headers = {
      'Accept': GITHUB_API_MIME_TYPE,
      'Authorization': f'Bearer {os.environ.get("GHAPI_PAT")}'
  }
  if size != 0:
    headers["Content-Length"] = str(size)
    headers["Content-Type"] = 'application/octet-stream'
  return headers


def fatal_error(msg):
  log.error(msg)
  exit()


assets = get_assets()

if len(assets) < 1:
  fatal_error('No assets found')

release = create_release(assets)

log.info(f'  release page created:')
log.info(f'    id: {release.get("id")}')
log.info(f'    url: {release.get("html_url")}')
log.info(f'    tag_name: {release.get("tag_name")}')

upload_assets(assets, release)

log.info('  release completed successfully')
