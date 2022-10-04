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

set -e

# Installs new software on a node in a gamma camera network.

# Select the identity config based on the hostname.
node_id_config=staging/config/identity-${HOSTNAME}.gin
echo "Selecting ${node_id_config} on ${HOSTNAME}"
mv ${node_id_config} staging/config/identity.gin
rm staging/config/identity-*.gin
cp -a staging/* -t ccline
for s in ccline uiline; do
  sudo cp staging/services/${s}.service /etc/systemd/system/
done

echo "Recreating venv on ${HOSTNAME}"
if [[ -d .venv/gamma ]]; then
  rm -rf .venv/gamma
fi
python -m venv ~/.venv/gamma
. ~/.venv/gamma/bin/activate

python -m pip install -r ccline/requirements.txt
python -m pip install --editable ccline/

echo "Starting services on ${HOSTNAME}"
sudo systemctl daemon-reload
for s in ccline uiline; do
  sudo service ${s} start
  sudo systemctl enable ${s}
done
