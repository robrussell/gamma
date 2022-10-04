#!/usr/bin/env bash
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

# Example script to use ssh-copy-id to send the host key to all nodes.

set -e

# This list will likely be the same as the list in the gin config but this
# script sends the gin config out so it shouldn't rely on those values.
nodes="10.20.0.1 10.20.0.2 10.20.0.3 10.20.0.4 10.20.0.5 10.20.0.6"

# This can give a patch of new lines for the known_hosts.
# ssh-keyscan -t rsa,dsa,ecdsa,ed25519 ${nodes} | sort -u - ~/.ssh/known_hosts | diff ~/.ssh/known_hosts -

echo "Known host lines for nodes. Add to ~/.ssh/known_hosts."
ssh-keyscan -t ed25519 ${nodes} 2>&1 | sort -u | grep --invert-match "^# "

# Uses ssh-copy-id to copy the public key id_rsa to each node.
# If ~/.ssh/id_rsa doesn't exist create it with ssh-keygen before running.
for n in ${nodes}; do
  echo "Node ${n}."
  ssh-copy-id -i ~/.ssh/id_rsa "pi@${n}"
done
