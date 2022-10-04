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

from absl import app, flags

from ccline import client, server

flags.DEFINE_bool("server", False, "Start a server.")
flags.DEFINE_bool("client", False, "Send a client command.")
flags.mark_bool_flags_as_mutual_exclusive(["server", "client"])

FLAGS = flags.FLAGS


def main(argv) -> None:
    del argv  # Unused.
    # Default to client if neither flag is given.
    if not FLAGS.server:
        client.run()
        return
    server.run()


if __name__ == "__main__":
    app.run(main)
