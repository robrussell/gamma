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

import asyncio
import os
import unittest
from unittest import mock

import gin
from absl import logging

from ccline import ccline_pb2
from ccline.server import Node


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        gin.parse_config_files_and_bindings(
            [os.path.join(os.getcwd(), "tests", "config", "test-single.gin")],
            [],
            skip_unknown=True,
        )

    @mock.patch("ccline.ccline_pb2_grpc.NodeStub")
    def test_goose(self, mock_node):
        node1 = Node("test_node_1", "test_node_1")
        request = ccline_pb2.GooseRequest()
        context = mock.MagicMock()
        reply = asyncio.run(node1.Goose(request, context))
        self.assertEqual(reply.message, "Goose!")
        node2 = Node("test_node_2", "test_node_1")
        reply = asyncio.run(node2.Goose(request, context))
        self.assertEqual(reply.message, "Duck!")

    @mock.patch("ccline.cli_runner.CliRunner.run_start_collection_cmd")
    @mock.patch("ccline.cli_runner.CliRunner.set_collection_path")
    def test_record(self, mock_set_path, mock_start_cmd):
        node1 = Node("test_node_1", "test_node_1")
        request = ccline_pb2.RecordRequest()
        request.data_path = "test-data-path-for-run"
        request.start_sensor_ids.append(ccline_pb2.Camera1)
        context = mock.MagicMock()
        reply = asyncio.run(node1.Record(request, context))
        mock_set_path.assert_called()
        mock_start_cmd.assert_called()

    @mock.patch("ccline.cli_runner.CliRunner.run_shutdown_cmd")
    def test_shutdown(self, mock_start_cmd):
        node1 = Node("test_node_1", "test_node_1")
        request = ccline_pb2.ShutdownRequest()
        context = mock.MagicMock()
        reply = asyncio.run(node1.Shutdown(request, context))
        mock_start_cmd.assert_called()


if __name__ == "__main__":
    unittest.main()
