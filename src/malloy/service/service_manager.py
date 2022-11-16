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

# service_manager.py

import asyncio
import logging
import platform
import re
from pathlib import Path

import grpc

import malloy.services.v1.compiler_pb2_grpc


class ServiceManager:
    _internal_service = "localhost:14310"

    @staticmethod
    def service_path():
        service_name = 'malloy-service'
        system = platform.system()
        if system == "Windows":
            service_name += "-win"
        elif system == "Linux":
            service_name += "-linux"
        elif system == "Darwin":
            service_name += "-macos"

        arch = platform.machine()
        if arch == "x86_64" or system == "Darwin" or system == "Windows":
            service_name += "-x64"
        elif arch == "arm64":
            service_name += "-arm64"

        if system == "Windows":
            service_name += ".exe"

        service_path = "{}".format(
            Path(Path(__file__).parent, service_name).resolve())
        return service_path

    def __init__(self, external_service=None):
        self._log = logging.getLogger(__name__)
        self._is_ready = asyncio.Event()
        self._external_service = external_service
        self._proc = None

    def is_ready(self):
        return self._is_ready.is_set()

    async def get_service(self):
        if not self._is_ready.is_set():
            await self._spawn_service()

        if self._external_service is None:
            return self._internal_service
        return self._external_service

    async def _spawn_service(self):
        if self._external_service is not None:
            self._log.debug('Using external service: {}'.format(
                self._external_service))
            self._is_ready.set()
            return

        service_path = ServiceManager.service_path()
        self._log.debug("Starting compiler service: {}".format(service_path))

        self._proc = await asyncio.create_subprocess_exec(
            service_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)

        service_listening = re.compile(r'^Server listening on (\d+)$')
        line = await self._proc.stdout.readline()
        if line is not None:
            sline = line.decode().rstrip()
            if service_listening.match(sline):
                self._log.debug(
                    "Compiler service is running: {}".format(sline))
                self._is_ready.set()
            else:
                self._log.debug(
                    "Compiler service NOT running: {}".format(sline))

    def _kill_service(self):
        if self._proc is None:
            return
        self._proc.kill()
