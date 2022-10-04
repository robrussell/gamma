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

import os
import gin
import unittest

from ccline.config import Config
from ccline.resolver import Resolver


def read_config(gin_configs: list[str], gin_bindings: list[str]):
    gin.clear_config()
    gin.parse_config_files_and_bindings(
        [os.path.join(os.getcwd(), "tests", "config", c) for c in gin_configs],
        gin_bindings,
        skip_unknown=True,
    )


class TestConfig(unittest.TestCase):

    def test_config_file(self):
        read_config(["test.gin"], [])
        resolver = Resolver()
        self.assertEqual(resolver.name_to_ip["name1"], "127.0.0.1")
        self.assertEqual(resolver.name_to_ip["name2"], "127.0.0.2")

    def test_config_bindings(self):
        read_config(["test.gin"], gin_bindings=["Config.coordinator_node_id='cnd'"])
        config = Config()
        self.assertEqual(config.coordinator_node_id, "cnd")


if __name__ == "__main__":
    unittest.main()
