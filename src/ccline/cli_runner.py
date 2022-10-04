# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Wrapper to hold overridable commands spawned through the shell. 

There are a lot of tools that are most easily accessed through the shell. 
This class isolates other classes from details of launching process, shell 
environment variables, and parsing shell command output. All the commands
are ultimately stored in gin config files which makes it easy to swap them
out for simulation, testing, or a different underlying distro.

The CliRunner should not be used to pass through arbitrary commands to a
shell on the system. When a native Python library is available it is
preferred and hopefully over time the CliRunner will eventually shrink in
favour of Python implementations.
"""

import dataclasses
import os
import subprocess
from shlex import quote

import gin


@gin.configurable()
@dataclasses.dataclass
class CliRunner:
    # Command line to start recording images.
    camera_video_cmd: list[str] | object = gin.REQUIRED

    # Command line to save a single image.
    camera_live_sample_cmd: list[str] | object = gin.REQUIRED

    # Command for dig nameserver lookup or equivalent.
    dig_cmd: str | object = gin.REQUIRED

    # Command for shutting down the machine.
    shutdown_cmd: str | object = gin.REQUIRED

    # Environment variables for most commands.
    # TODO: Add to config.
    # default_env: dict[str, str]|object = gin.REQUIRED
    # default_env: dict[str, str] = {'DISPLAY': ':0.0'}
    default_env = {"DISPLAY": ":0.0"}

    # Root directory for all data that will be saved during operation.
    base_collection_path: str | object = gin.REQUIRED

    def __post_init__(self) -> None:
        # Path relative to base_collection_ path.
        self.collection_path_: str = "nocollection"

    def run_dig_cmd(self, hostname: str) -> str:
        assert isinstance(self.dig_cmd, str)
        # See caveat at https://docs.python.org/3.10/library/shlex.html#shlex.quote
        proc = subprocess.run(
            self.dig_cmd.format(hostname=quote(hostname)),
            env=self.default_env,
            shell=True,
            capture_output=True,
            check=True,
            text=True,
        )
        return proc.stdout.strip()

    def run_live_sample_cmd(self) -> subprocess.Popen:
        """Spawns shell command to capture a single image.

        Returns: The started process. It will likely end very soon after returning.

        """
        assert isinstance(self.camera_live_sample_cmd, list)
        directory = self.get_full_nocollection_path()
        os.makedirs(directory, exist_ok=True)
        # TODO: For the live sample it would be useful to capture logs from this command.
        process = subprocess.Popen(
            self.camera_live_sample_cmd, env=self.default_env, cwd=directory
        )
        return process

    def run_start_collection_cmd(self) -> subprocess.Popen:
        """Spawns shell command to start imagery collection.

        Returns: The started process. Pass the process to stop_collection_cmd() to end it.

        """
        assert isinstance(self.camera_video_cmd, list)
        directory = self.get_full_collection_path()
        os.makedirs(directory, exist_ok=True)
        process = subprocess.Popen(
            self.camera_video_cmd, env=self.default_env, cwd=directory
        )
        return process

    def stop_collection_cmd(self, process: subprocess.Popen):
        """Kills the given collection process and resets the collection path.

        TODO: Should be able to use a signal other than kill.
        """
        if process:
            process.kill()
        self.collection_path_ = "nocollection"

    def run_shutdown_cmd(self) -> subprocess.Popen:
        """Wrapper for shutdown.

        Returns: The started process. If this process ends then it likely means
        that shutdown has failed.

        """
        assert isinstance(self.shutdown_cmd, str)
        process = subprocess.Popen(self.shutdown_cmd, env=self.default_env)
        return process

    def get_full_nocollection_path(self):
        """Returns the absolute path to the `nocollection` directory.

        Given this structure:
        `/home/pi/data/`
          * `calibration_C/`
          * `collection_L/`
          * `nocollection/`

        Will return '/home/pi/data/nocollection'.
        """
        return os.path.join(f"{self.base_collection_path}", "nocollection/")

    def get_full_collection_path(self):
        """Returns the absolute path to the current collection directory.

        Given this structure:
        `/home/pi/data/`
          * `calibration_C/`
          * `collection_L1/`
          * `collection_L2/`
          * `nocollection/`

        Will return '/home/pi/data/collection_L2' during collection L2 or
        '/home/pi/data/nocollection' after it ends.
        """
        return os.path.join(f"{self.base_collection_path}", f"{self.collection_path_}/")

    def set_collection_path(self, collection_path: str):
        assert isinstance(self.collection_path_, str)
        self.collection_path_ = collection_path
