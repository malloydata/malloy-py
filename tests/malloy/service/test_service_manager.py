# Copyright 2022 Google LLC
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

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
@pytest.mark.skipif(not Path(ServiceManager.service_path()).exists(), reason="Could not find: {}".format(ServiceManager.service_path()))
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
