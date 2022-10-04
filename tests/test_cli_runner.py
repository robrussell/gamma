#!/usr/bin/env python3
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

import gin
import os
import unittest
from unittest import mock

from ccline.cli_runner import CliRunner
from ccline.config import Config
from ccline.resolver import Resolver


def read_config(gin_configs: list[str], gin_bindings: list[str]):
    gin.clear_config()
    gin.parse_config_files_and_bindings(
        [os.path.join(os.getcwd(), "tests", "config", c) for c in gin_configs],
        gin_bindings,
        skip_unknown=True,
    )


class TestCliRunner(unittest.TestCase):

    def test_resolve_name(self):
        read_config(
            ["test.gin"],
            gin_bindings=["CliRunner.dig_cmd = 'echo {hostname} some address'"],
        )
        cli_runner = CliRunner()
        address = cli_runner.run_dig_cmd("fake_host")
        self.assertEqual(address, "fake_host some address")
        address = cli_runner.run_dig_cmd("oops; ls *")
        self.assertEqual(address, "oops; ls * some address")

    @mock.patch("os.makedirs")
    @mock.patch("subprocess.Popen")
    def test_live_sample(self, mock_popen, mock_makedirs):
        read_config(
            ["test.gin"],
            gin_bindings=[
                "CliRunner.base_collection_path = '/gamma/data'",
                "CliRunner.camera_live_sample_cmd = ['echo', 'no live_sample_cmd']",
            ],
        )
        cli_runner = CliRunner()
        process = cli_runner.run_live_sample_cmd()
        expected_path = os.path.join("/", "gamma", "data", "nocollection/")
        mock_makedirs.assert_called_with(expected_path, exist_ok=True)
        mock_popen.assert_called_with(
            ["echo", "no live_sample_cmd"], env=mock.ANY, cwd=expected_path
        )

    @mock.patch("os.makedirs")
    @mock.patch("subprocess.Popen")
    def test_start_collection(self, mock_popen, mock_makedirs):
        read_config(
            ["test.gin"],
            gin_bindings=[
                "CliRunner.base_collection_path = '/gamma/data'",
                "CliRunner.camera_video_cmd = ['echo', 'collect now']",
            ],
        )
        cli_runner = CliRunner()
        cli_runner.set_collection_path("leaf")
        process = cli_runner.run_start_collection_cmd()
        expected_path = os.path.join("/", "gamma", "data", "leaf/")
        mock_makedirs.assert_called_with(expected_path, exist_ok=True)
        mock_popen.assert_called_with(
            ["echo", "collect now"], env={"DISPLAY": ":0.0"}, cwd=expected_path
        )


if __name__ == "__main__":
    unittest.main()
