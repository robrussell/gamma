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

# Warning: This is only an example and should not be run as-is. Edit to suit
#          your specific network and machine configuration.
#
# Example deploy script to collect local source files. Copies the files to
# multiple nodes via rsync, then install and restart the services.
#
# Expects to be run as:
# ./deploy/deploy.sh
set -e

# This list will likely be the same as the list in the gin config but this
# script sends the gin config out so it shouldn't rely on those values.
nodes="10.20.0.1 10.20.0.2 10.20.0.3 10.20.0.4 10.20.0.5 10.20.0.6"

# This can give a list of new lines for the known_hosts file to avoid extra
# prompts when connecting.
#ssh-keyscan -t rsa,dsa,ecdsa,ed25519 ${nodes} | sort -u - ssh_known_hosts | diff ~/.ssh/known_hosts

# Pings all camera nodes in parallel.
function ping_all_nodes() {
  echo "${nodes}" | xargs -n1 -P0 ping -c 2
}

# Collects the latest files into deploy/staging/<datestamp> and symlinks the
# path as deploy/staging/latest for later use.
function gather_latest() {
  root_path="$(pwd)"
  root_deploy="${root_path}/deploy"
  if [[ ! -d "${root_deploy}" ]]; then
    echo "Run from directory above deploy/."
    exit -1
  fi
  staging_root="${root_deploy}/staging"
  build_tag=$(date +%s)
  mkdir -p ${staging_root}/s-${build_tag}
  ln -sf ${staging_root}/s-${build_tag} --no-target-directory ${staging_root}/latest
  echo "Latest is ${staging_root}/s-${build_tag}"
  # Another option would be to use --files-from to provide a list of files.
  rsync -az \
    --exclude-from "${root_deploy}/rsync-exclude" \
    "${root_deploy}/preparetarget.sh" \
    "${root_deploy}/updatetarget.sh" \
    "${root_path}/config" \
    "${root_path}/services" \
    "${root_path}/src" \
    "${root_path}/scripts" \
    "${root_path}/requirements.txt" \
    "${root_path}/setup.py" \
    ${staging_root}/latest/
}

# Sends files from `staging/latest` to the `staging` path on each node. The
# updatetarget.sh script runs on the target first then files are sent to the node, then preparetarget.sh runs
# on the target.
# Requires an ip address (or ssh/rsync hostname) as an argument.
function update_node() {
  echo "Running backup target script on ${1}"
  # TODO: Untested
  rsync -az --delete ${staging_root}/latest/preparetarget.sh pi@${1}:preparetarget.sh
  ssh pi@${1} staging/updatetarget.sh
  echo "Syncing ${staging_root} to ${1}:staging/"
  rsync -az --delete ${staging_root}/latest/ pi@${1}:staging/
  echo "Running prepare target script on ${1}"
  ssh pi@${1} staging/preparetarget.sh
}

# Runs the shutdown command on the given node.
# Requires an ip address (or ssh hostname) as an argument.
function shutdown_node() {
  ssh pi@${1} shutdown -h 0 now
}

export -f update_node
export -f shutdown_node
export staging_root

ping_all_nodes
gather_latest

# Run the sync in parallel by calling update_node with all node addresses.
echo "${nodes}" | xargs -n1 -P0 bash -c 'update_node "$@"' _
#echo "${nodes}" | xargs -n1 -P0 bash -c 'shutdown_node "$@"' _
