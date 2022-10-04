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

from typing import Dict

import gin

from ccline.cli_runner import CliRunner


@gin.configurable()
class Resolver:
    """Access functions to find camera node resources by node name."""

    def __init__(
        self,
        name_to_ip: Dict[str, str] = {},
        name_to_port: Dict[str, str] = {},
        probe=False,
    ):
        """Access functions to find camera node resources by node name.

        Args:
          name_to_ip: Dictionary of node IP addresses keyed by node names.
          name_to_port: Dictionary of node port keyed by node names.
          probe: True to check for connectivity and remove unresponsive nodes.
        """
        self.name_to_ip = name_to_ip
        self.name_to_port = name_to_port
        print(self.name_to_ip)
        print(self.name_to_port)
        # Overwrite with just the ones that are found.
        if probe:
            self.name_to_ip = self.probe_nodes(self.name_to_ip.keys())

    def all_nodes(self):
        return self.name_to_ip.keys()

    def probe_nodes(self, probe_names):
        probed_name_to_ip = {}
        cli_runner = CliRunner()
        for hostname in probe_names:
            ip_address = cli_runner.run_dig_cmd(hostname)
            print(f"{hostname} : {ip_address}")
            probed_name_to_ip[hostname] = ip_address
        return probed_name_to_ip

    def address_for_name(self, name: str, listen: bool = False) -> str:
        """Gives the address with port for the given node name.

        Args:
          name:
          listen: `True` for the server. Leave `False` when connecting.

        Returns:
          String to use when opening GRPC connection.
        """
        if listen:
            return f"[::]:{self.name_to_port[name]}"
        else:
            return f"{self.name_to_ip[name]}:{self.name_to_port[name]}"
