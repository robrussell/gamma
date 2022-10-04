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

"""Command line client for interacting with the ccline server."""

import asyncio
from typing import Optional

import grpc
from absl import app, flags, logging

from ccline import ccline_pb2, ccline_pb2_grpc
from ccline.config import Config, read_config, timestamp_stub
from ccline.resolver import Resolver

flags.DEFINE_enum(
    "cmd",
    None,
    ["start", "stop", "sample", "shutdown"],
    "Send commands to all nodes in the array.",
)

flags.DEFINE_string("recording_id", None, "Text name for the recording.")

flags.DEFINE_string("target_node_id", None, "Name of the node for this request.")

FLAGS = flags.FLAGS

CHANNEL_OPTIONS = [
    ("grpc.lb_policy_name", "pick_first"),
    ("grpc.enable_retries", 0),
    ("grpc.keepalive_timeout_ms", 10000),
]


async def find_coordinator(resolver: Resolver):
    coordinator = None
    for candidate in resolver.all_nodes():
        print(f"Candidate {candidate} {resolver.address_for_name(candidate)}")
        async with grpc.aio.insecure_channel(
            target=resolver.address_for_name(candidate), options=CHANNEL_OPTIONS
        ) as channel:
            node = ccline_pb2_grpc.NodeStub(channel)
            request = ccline_pb2.GooseRequest()
            print(f"Sending {candidate} request {request}")
            response = await node.Goose(request, timeout=2)
        print(f"From {candidate} Received {response.message}")
        if response.message == "Goose!":
            coordinator = candidate
    return coordinator


async def request_sample(target_node_id: str, resolver: Resolver):
    print(
        f"Sample from {target_node_id} {resolver.address_for_name(target_node_id)}"
    )
    async with grpc.aio.insecure_channel(
        target=resolver.address_for_name(target_node_id), options=CHANNEL_OPTIONS
    ) as channel:
        node = ccline_pb2_grpc.NodeStub(channel)
        response = await node.LiveSample(ccline_pb2.LiveSampleRequest(), timeout=10)
    print(f"From {target_node_id}")
    with open(f"sample-{target_node_id}.jpg", "wb") as f:
        f.write(response.image)


async def start_collecting(
    coordinator: str,
    resolver: Resolver,
    recording_id: str,
    recording_tag: Optional[str] = None,
) -> None:
    print(
        f"Start collecting {coordinator}, {resolver.address_for_name(coordinator)}"
    )
    async with grpc.aio.insecure_channel(
        target=resolver.address_for_name(coordinator), options=CHANNEL_OPTIONS
    ) as channel:
        goose = ccline_pb2_grpc.CoordinatorStub(channel)
        request = ccline_pb2.StartCollectingRequest()
        if recording_id is None:
            logging.fatal("Missing required recording_id.")
        request.recording_id = recording_id
        if recording_tag is not None:
            request.recording_tag.append(recording_tag)
        response = await goose.StartCollecting(request, timeout=10)
    print(f"Start collecting response: {response.message}")


async def stop_collecting(coordinator: str, resolver: Resolver) -> None:
    async with grpc.aio.insecure_channel(
        target=resolver.address_for_name(coordinator), options=CHANNEL_OPTIONS
    ) as channel:
        goose = ccline_pb2_grpc.CoordinatorStub(channel)
        _ = await goose.StopAllCollects(ccline_pb2.StopAllCollectsRequest(), timeout=10)
    print("Stopped collecting")


async def shutdown(coordinator: str, resolver: Resolver) -> None:
    print(f"Client sending shutdown to {resolver.address_for_name(coordinator)}")
    async with grpc.aio.insecure_channel(
        target=resolver.address_for_name(coordinator), options=CHANNEL_OPTIONS
    ) as channel:
        goose = ccline_pb2_grpc.CoordinatorStub(channel)
        _ = await goose.ShutdownCluster(ccline_pb2.ShutdownClusterRequest())
    print("Shutdown sent from client")


def run():
    flags.mark_flag_as_required("cmd")
    read_config()
    config = Config()
    command = FLAGS.cmd
    recording_id = FLAGS.recording_id
    if recording_id is None:
        recording_id = f"r_{timestamp_stub()}"
    resolver = Resolver()
    print(f"Command {command}, recording_id {recording_id}")
    coordinator_commands = ["start", "stop", "shutdown"]
    if command in coordinator_commands:
        coordinator = asyncio.run(find_coordinator(resolver=resolver))
        if coordinator is None:
            logging.fatal("Could not find coordinator.")
            exit()
        if command == "start":
            print(
                f"Start command {coordinator}, {resolver.address_for_name(coordinator)}"
            )
            asyncio.run(start_collecting(coordinator, resolver, recording_id))
        if command == "stop":
            asyncio.run(stop_collecting(coordinator, resolver))
        if command == "shutdown":
            asyncio.run(shutdown(coordinator, resolver))
    if command == "sample":
        target_node_id = config.target_node_id
        if target_node_id is None:
            flags.mark_flag_as_required("target_node_id")
        target_node_id = FLAGS.target_node_id
        asyncio.run(request_sample(target_node_id, resolver=resolver))


def main(argv) -> None:
    del argv  # Unused.
    run()


if __name__ == "__main__":
    app.run(main)
