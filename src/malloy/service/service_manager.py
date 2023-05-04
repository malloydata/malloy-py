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

# service_manager.py
"""Module manages the service(s) needed by the Malloy runtime. """
import asyncio
import logging
import platform
import re
from pathlib import Path


class ServiceManager:
  """A class that manages the connection to a Malloy compiler service. """
  _internal_service = "localhost:14310"

  @staticmethod
  def service_path():
    service_name = "malloy-service"
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

    service_path = f"{Path(Path(__file__).parent, service_name).resolve()}"
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
      self._log.debug("Using external service: %s", self._external_service)
      self._is_ready.set()
      return

    service_path = ServiceManager.service_path()
    self._log.debug("Starting compiler service: %s", service_path)

    self._proc = await asyncio.create_subprocess_exec(
        service_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)

    service_listening = re.compile(r"^Server listening on (\d+)$")
    line = await self._proc.stdout.readline()
    if line is not None:
      sline = line.decode().rstrip()
      if service_listening.match(sline):
        self._log.debug("Compiler service is running: %s", sline)
        self._is_ready.set()
      else:
        self._log.debug("Compiler service NOT running: %s", sline)

  def _kill_service(self):
    if self._proc is None:
      return
    self._proc.kill()
