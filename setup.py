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

from setuptools import setup, find_packages

setup(
    name="gammacam",
    version="0.0.1",
    description="Flexible camera array control and logging.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "absl-py>=1.2.0",
        "gin-config>=0.5.0",
        "grpcio==1.44.0",
        "grpcio-tools==1.44.0",
        "protobuf>=3.20.2",
    ],
)
