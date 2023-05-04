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

# test_service_manager.py

import pytest
import asyncio
from pathlib import Path

from malloy.service import ServiceManager


def test_is_ready_is_false_when_not_ready():
  sm = ServiceManager()
  assert sm.is_ready() == False


def test_is_ready_is_false_when_external_service_not_ready():
  sm = ServiceManager(external_service="localhost:54321")
  assert sm.is_ready() == False


@pytest.mark.asyncio
@pytest.mark.skipif(not Path(ServiceManager.service_path()).exists(),
                    reason="Could not find: {}".format(
                        ServiceManager.service_path()))
async def test_returns_local_service():
  sm = ServiceManager()
  service = await sm.get_service()
  assert service == sm._internal_service
  assert sm.is_ready()
  sm._kill_service()
  await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_returns_external_service_if_provided():
  external_service = "localhost:54321"
  sm = ServiceManager(external_service=external_service)
  service = await sm.get_service()
  assert sm.is_ready()
  assert service == external_service


def test_kill_service_does_not_throw_if_no_proc_started():
  sm = ServiceManager()
  sm._kill_service()
