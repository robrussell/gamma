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

"""The ccline server.

Implements the Node and Coordinator interfaces.
"""

import asyncio
import os
from signal import SIGTERM, signal

import grpc
from absl import app, flags

from ccline import ccline_pb2, ccline_pb2_grpc
from ccline.cli_runner import CliRunner
from ccline.config import Config, read_config
from ccline.resolver import Resolver

FLAGS = flags.FLAGS


class Node(ccline_pb2_grpc.NodeServicer):
    """The Node server runs on every participant in the flexible camera array.

    External users send most requests to the coordinator but specific requests
    may target the node.
    """

    def __init__(self, my_id: str, coordinator_id: str):
        self.node_id = my_id
        self.coordinator_id = coordinator_id
        self.is_coordinator = self.coordinator_id == self.node_id
        self.collection_process = None
        print(f"Starting node {my_id} coordinator {coordinator_id}")

    async def Goose(
        self, request: ccline_pb2.GooseRequest, context: grpc.aio.ServicerContext
    ) -> ccline_pb2.GooseReply:
        if self.is_coordinator:
            print("Goose")
            return ccline_pb2.GooseReply(id=self.coordinator_id, message="Goose!")
        else:
            print("Duck")
            return ccline_pb2.GooseReply(id=self.coordinator_id, message="Duck!")

    async def Record(
        self, request: ccline_pb2.RecordRequest, context: grpc.aio.ServicerContext
    ) -> ccline_pb2.RecordReply:
        print("Record on node %s", self.node_id)
        print("  Turn on %s", request.start_sensor_ids)
        print("  Turn off %s", request.stop_sensor_ids)
        print(f"Received Record on {self.node_id}")
        cli_runner = CliRunner()
        if request.data_path:
            cli_runner.set_collection_path(request.data_path)
        # TODO: This needs to be refined. The Record command should handle the
        # lists of sensors to start and stop then run the appropriate commands
        # for each sensor or group of sensors. For now we just run one command
        # to start recording as long as any sensors are asked to start. And if
        # not then all sensors are stopped.
        if request.start_sensor_ids:
            self.collection_process = cli_runner.run_start_collection_cmd()
        else:
            self.collection_process = cli_runner.stop_collection_cmd(
                self.collection_process
            )
        return ccline_pb2.RecordReply()

    async def LiveSample(
        self, request: ccline_pb2.LiveSampleRequest, context: grpc.aio.ServicerContext
    ) -> ccline_pb2.LiveSampleReply:
        print(
            "LiveSample on node %s, sensors %s", self.node_id, request.sensor_ids
        )
        cli_runner = CliRunner()
        process = cli_runner.run_live_sample_cmd()
        process.wait()
        # TODO: 'live_sample.jpg' must match the config file. Name should be returned from cli_runner.
        filename = os.path.join(
            cli_runner.get_full_nocollection_path(), "live_sample.jpg"
        )
        content = None
        with open(filename, "rb") as f:
            content = f.read()
        return ccline_pb2.LiveSampleReply(image=content)

    async def Shutdown(
        self, request: ccline_pb2.ShutdownRequest, context: grpc.aio.ServicerContext
    ) -> ccline_pb2.ShutdownReply:
        print(f"Received shutdown on node {self.node_id}")
        cli_runner = CliRunner()
        _ = cli_runner.run_shutdown_cmd()
        return ccline_pb2.ShutdownReply()


class Coordinator(ccline_pb2_grpc.CoordinatorServicer):
    """The coordinator (goose) handles tasks targetted at the camera array.

    External hosts find the coordinator and communicate directly with it for
    tasks like starting and stopping requests. The coordinator relays the task
    and results to and from all nodes.
    """

    def __init__(self, resolver: Resolver):
        self.resolver = resolver

    async def StartCollecting(
        self,
        request: ccline_pb2.StartCollectingRequest,
        context: grpc.aio.ServicerContext,
    ) -> ccline_pb2.StartCollectingReply:
        print("StartCollecting")
        print("  Recording ID %s", request.recording_id)
        # Start clients for all nodes, including itself.
        for node in self.resolver.all_nodes():
            async with grpc.aio.insecure_channel(
                target=self.resolver.address_for_name(node)
            ) as channel:
                client = ccline_pb2_grpc.NodeStub(channel)
                record_request = ccline_pb2.RecordRequest()
                # TODO: The coordinator doesn't have a way to choose which cameras
                # or sensors to select here yet.
                record_request.start_sensor_ids.append(ccline_pb2.Camera1)
                record_request.data_path = request.recording_id
                print(f"Sending Record to {node}: record_request {record_request}")
                response = await client.Record(record_request)
            print(f"Record {node} response: {response}")
        return ccline_pb2.StartCollectingReply(
            result=StartCollectingResult.OK, message="All sensors started."
        )

    async def StopAllCollects(
        self,
        request: ccline_pb2.StopAllCollectsRequest,
        context: grpc.aio.ServicerContext,
    ) -> ccline_pb2.StopAllCollectsReply:
        print("StopAllCollects")
        # Start clients for all nodes, including itself.
        for node in self.resolver.all_nodes():
            async with grpc.aio.insecure_channel(
                target=self.resolver.address_for_name(node)
            ) as channel:
                client = ccline_pb2_grpc.NodeStub(channel)
                record_request = ccline_pb2.RecordRequest()
                record_request.stop_sensor_ids.extend([
                    ccline_pb2.Camera1,
                    ccline_pb2.Camera2,
                    ccline_pb2.Camera3,
                    ccline_pb2.Camera4,
                    ccline_pb2.Imu1,
                    ccline_pb2.Imu2,
                    ccline_pb2.Imu3,
                    ccline_pb2.Imu4,
                ])
                response = await client.Record(record_request, timeout=10)
            print(f"Record {node} response: {response}")
        return ccline_pb2.StopCollectingReply()

    async def ShutdownCluster(
        self,
        request: ccline_pb2.ShutdownClusterRequest,
        context: grpc.aio.ServicerContext,
    ) -> ccline_pb2.ShutdownClusterReply:
        print("Shutdown all nodes")
        # This implementation shuts down all nodes in any order. However some nodes
        # may play a specific role in connecting back to the client. It would be
        # preferable to shut down that node last.
        for node in self.resolver.all_nodes():
            print(f"Sending shutdown to {node}")
            async with grpc.aio.insecure_channel(
                target=self.resolver.address_for_name(node)
            ) as channel:
                client = ccline_pb2_grpc.NodeStub(channel)
                record_request = ccline_pb2.ShutdownRequest()
                response = await client.Shutdown(record_request, timeout=10)
            print(f"Shutdown {node} response: {response}")
        reply = ccline_pb2.ShutdownClusterReply()
        return reply


def create_server(
    my_id: str, coordinator_id: str, resolver: Resolver
) -> grpc.aio.Server:
    """Factory to create a GRPC server.

    Args:
      my_id: Network-unique name for the node. Normally matches the hostname, if any.
      coordinator_id: Name of the goose - the node that receives requests for the array.
      resolver: Maps names to IPs for the array.
    """
    new_server = grpc.aio.server()
    ccline_pb2_grpc.add_NodeServicer_to_server(Node(my_id, coordinator_id), new_server)
    if my_id == coordinator_id:
        # This node is the coordinator. Start up a coordinator server to answer
        # external requests.
        print(f"Coordinator service on {my_id}")
        ccline_pb2_grpc.add_CoordinatorServicer_to_server(
            Coordinator(resolver), new_server
        )
    listen_address = resolver.address_for_name(my_id, listen=True)
    port_num = new_server.add_insecure_port(listen_address)
    print(f"Created server {my_id} on {listen_address}")
    return new_server


async def serve(my_id: str, coordinator_id: str, resolver: Resolver) -> grpc.aio.Server:
    """Creates, starts, and returns a GRPC server.

    Args:
      my_id: Network-unique name for the node. Normally matches the hostname, if any.
      coordinator_id: Name of the goose - the node that receives requests for the array.
      resolver: Maps names to IPs for the array.
    """
    new_server = create_server(my_id, coordinator_id, resolver)
    await new_server.start()

    # TODO: Only works on main thread.
    async def handle_sigterm(*_):
        print(f"Server {my_id} received shutdown signal")
        await new_server.stop(10.0)
        print("Shut down gracefully")

    signal(SIGTERM, handle_sigterm)

    return new_server


async def serve_and_block(my_id: str, coordinator_id: str, resolver: Resolver):
    new_server = await serve(my_id, coordinator_id, resolver)
    await new_server.wait_for_termination()


def run():
    read_config()
    config = Config()
    resolver = Resolver()
    assert isinstance(config.node_id, str)
    assert isinstance(config.coordinator_node_id, str)
    _ = asyncio.run(
        serve_and_block(config.node_id, config.coordinator_node_id, resolver)
    )


def main(argv) -> None:
    del argv  # Unused.
    run()


if __name__ == "__main__":
    app.run(main)
