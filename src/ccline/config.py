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

"""Camera logger core.

Common code shared between server and client.
"""

import dataclasses
import os
from datetime import datetime, timezone
from typing import Optional

import gin
from absl import flags

flags.DEFINE_string(
    "node_id",
    None,
    (
        "Friendly identifier for the node. Probably the hostname."
        "Definitely determines the port number."
    ),
)
flags.DEFINE_multi_string("gin_bindings", None, "Gin parameter bindings.")
flags.DEFINE_multi_string("gin_configs", None, "Gin config files.")
flags.DEFINE_string("config_dir", None, "Directory containing gin config files.")

FLAGS = flags.FLAGS


@gin.configurable()
@dataclasses.dataclass
class Config:
    """Configuration flags for everything."""

    node_id: Optional[str] = None
    coordinator_node_id: Optional[str] = None
    # Node to receive the given command.
    target_node_id: Optional[str] = None


def timestamp_stub() -> str:
    return str(int(datetime.now(timezone.utc).timestamp()))


def read_config():
    gin_files = FLAGS.gin_configs
    config_base = FLAGS.config_dir
    if config_base is None:
        config_base = os.path.join(os.getcwd(), "config")
    gin.clear_config()
    gin_configs = [os.path.join(config_base, f) for f in gin_files]
    print("configs", gin_configs)
    gin_bindings = FLAGS.gin_bindings
    print("bindings", gin_bindings)
    gin.parse_config_files_and_bindings(gin_configs, gin_bindings, skip_unknown=True)
