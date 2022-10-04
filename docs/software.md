The Gamma Camera software environment is mainly contained in the Python library `ccline`. Other directories in the project repo hold mechanical designs, support code, tests, and examples.

# Setting up for development

There can be quite a few computers involved with the gamma flexible camera array. To keep it clear the term _workstation_ is used to refer to the computer that you type on or the one that's generally outside the camera array (even if that computer is a laptop or yet another Raspberry Pi). Each Raspberry Pi with a camera module is called a _node_ in the cammera array. The _workstation_ is not considered to be part of the camera array even though it is an occasional participant on the network.

1. First set up each individual Raspberry Pi with a camera module and ensure it works. 
2. Connect each node to the wired ethernet router. Plug your workstation into the router too.
3. Then proceed to set up the Gamma camera flexible camera array software. First install it on your workstation, then on each of the nodes.
4. After you're used to the software environment, try adapting the example deploy.sh to simplify development and iteration.

If you want to try it without hardware, see the simulation instructions below.

## Installing on the workstation

The workstation is the computer you're working at. Git clone the repo to your workstation into a directory such as `~/gamma`. The name of the path `~/gamma` isn't special. Just change the path in the examples if you decide to put it somewhere else.

## Install the Python package

Installing the gammacam package will make the `ccline` module available to any Python code running in the same virtualenv. It's only distributed as source for now.

These are minimal commands to install the gammacam library for development if you're already familiar with developing in a Python virtualenv:

```
cd ~/gamma
python -m venv ~/.venv/gamma
. ~/.venv/gamma/bin/activate
python -m pip install --editable .
```

The package is named gammacam. It provides only the `ccline` module. Run:

```
python -c "import ccline"
```

If the installation is working then there will be no output.

### More details on virtualenv

The Python documentation has (a lot) more detail on [how to use virtual enviroments](https://docs.python.org/3/library/venv.html). Here are the basics for Gamma Camera.

Using a virtualenv can isolate the gammacam Python installation along with the dependencies it needs. This helps prevent interactions with other Python libraries on your system. It also means that libraries you want to use together all need to be installed in the same virtualenv.

1. Create the virtualenv (once)

```
python -m venv ~/.venv/gamma
```

2. Activate the virtualenv (once per terminal every session)

```
. ~/.venv/gamma/bin/activate
```

Don't miss the leading `.`. It's the same as [`source` in bash](https://www.gnu.org/software/bash/manual/bash.html#index-_002e). It has to be sourced so it can modify the current environment.

3. When you want to switch back to the system Python installation and stop using the virtualenv just close the terminal or deactivate the venv by running:

```
deactivate
```

4. To start over and recreate the virtualenv, delete it and recreate it.

```
deactivate
rm -rfI ~/.venv/gamma
python -m venv ~/.venv/gamma
```

## Compiling protocol buffers

The compiled protocol buffer files are `src/ccline/*_pb2.py` and `src/ccline/*_pb2_grpc.py`. They only need to be recompiled if the definitions in `proto/ccline/*.proto` change.

```bash
cd ~/gamma/src
python -m grpc_tools.protoc -I ../proto --python_out=. --grpc_python_out=. ../proto/ccline/*.proto
```

## Config files

The config files are under `config/*.gin`. They're written in the [Google Gin Config](https://github.com/google/gin-config) language.

Edit the names and IP addresses in `config/prod.gin` to suit your network. The config files contain the IP addresses, names, and commands used for each Raspberry Pi. The address range `10.20.0.1` to `10.20.0.6` and names `gamma1` through `gamma6` are used in the documentation and examples. These are only examples though and `ccline` only relies on the values supplied via configuration.

Each file named `identity-gamma<N>.gin` in the directory is used by the `deploy.sh` to provide a name for the node based on the hostname.

# Setting up each node

Set up ssh on all of the Raspberry Pis and ensure that you can log in from your workstation without entering passwords repeatedly. The `copy-key.sh` example script shows how to use [ssh-copy-id](https://www.ssh.com/academy/ssh/copy-id) to securely copy your ssh key to each node in the array.

## Send files to the nodes

Copy the `src`, `config`, `services`, `requirements.txt`, and `setup.py` directories to each Raspberry Pi. Cloning the gammacam git repo to each node is fine too, it will just have a lot of unneeded files.

As an example, the following commands will first copy the files we want to `deploy/staging` on the workstation and then copy them in parallel to all the Raspberry Pi nodes.

```
rsync --exclude-from='.gitignore' --mkpath -az src config services requirements.txt setup.py deploy/staging/
export NODES="10.20.0.1 10.20.0.2 10.20.0.3 10.20.0.4 10.20.0.5 10.20.0.6"
echo ${NODES} | xargs -n1 -P0 bash -c echo rsync --mkpath -az deploy/staging/ pi@_:staging/
```

Brief explanation of the command above:

`rsync`: A very efficient way to send and receive files over ssh. The `--exclude-from` uses the `.gitignore` file to skip files from the Python installation like the `.egg-info` directory.

`xargs`: Substitutes the node IP address where the `_` shows up and runs all the resulting commands in parallel (because of the `-P0` flag)

If your configuration or software changes frequently then you can use a more complete command line or script to send the configuration directory to all nodes. The script at [deploy/deploy.sh] is provided as a starting point. This script is only an incomplete example though, review it carefully before running to ensure it will work correctly in your environment.

## Dependencies to install on each node

```
sudo apt-get update
sudo apt-get install -y pip dnsutils python3-venv
```

## Install the package on the node

The installation on each Raspberry Pi is similar to the way the library is installed on the workstation. It needs to be installed on each node after the files are copied over. Use commands like these or adapt commands from `deploy.sh`.

```
cd ~
python -m venv ~/.venv/gamma
. ~/.venv/gamma/bin/activate
python -m pip install -r ccline/requirements.txt
python -m pip install --editable ccline/
```

Note that the paths here are used in the files under `services/*.service`.

### Manual Python library installation

Using `setup.py` or `requirements.txt` with `pip` is the easiest way to install deps. But if you have to install manually the `pip` command lines use similar syntax. In particular, if you run into a bug with glibc and Python GRPC on the Raspberry Pi it may be necessary to go back to an older version of `grpcio` and `grpcio-tools`:

```
pip uninstall -y grpcio grpcio-tools
pip install grpcio==1.44.0 --no-binary=grpcio
pip install grpcio-tools==1.44.0 --no-binary=grpcio-tools
```

### Extra dependencies for displays

Adafruit documents the dependencies needed for the hardware UI on the RPi. They're not included in the deps for the main library yet.

## Enable services to start at boot

Copy `ccline.service` to `/etc/systemd/system/` and start it. 

```
sudo service ccline start
```

Enable the service to make it start on every boot

```
sudo systemctl enable ccline
```

The node that has the user interface runs `ui.py` with the `uiline.service` file.

```
sudo service uiline start
sudo systemctl enable uiline
```

# Simulation

A dry-run or simulation is a good way to test out configuration changes without setting up all of the hardware. All the local commands and network parameters for gamma are stored in gin configuration files. This makes it easy to change the configuration and run a simulated set of nodes all on the workstation.

1. Set up the configuration for each simulated node.

  * The `dev.gin` config has some example parameters for a local dry-run. It sets up addresses on `localhost` with different port numbers.
  * Remember that the server **will create directories** to store data so set an appropriate location in `CliRunner.base_collection_path` via configuration. A good place is under the `jot/testing` folder.
  * Prefixing your production command with `echo` is a simple way to print or log the command that would run in the production config.

2. Start multiple servers.
  * If you do this a lot, using `screen`, `tmux`, or `iTerm2` can make it easier to manage multiple terminal windows at once or automate this kind of dry-run integration testing. For example, run these similar commands in four separate windows:

```bash
cd ~/gamma/
scripts/run.py --server --gin_configs dev.gin --gin_configs identity-gamma1.gin
```

```bash
cd ~/gamma/
scripts/run.py --server --gin_configs dev.gin --gin_configs identity-gamma2.gin
```

```bash
cd ~/gamma/
scripts/run.py --server --gin_configs dev.gin --gin_configs identity-gamma3.gin
```

```bash
cd ~/gamma/
scripts/run.py --server --gin_configs dev.gin --gin_configs identity-gamma4.gin
```

3. Run a command from a client.

```bash
scripts/run.py --gin_configs dev.gin --cmd start
```

Changing the config or source requires restarting all servers.

# Design

The design here is aspirational, not everything is implemented yet.

## Architectural components

1. An external host can connect to the camera array. The external host can issue commands and receive data. The external host is not generally considered a part of the camera system. It can connect and disconnect without impacting camera system operation. There is generally expected to be only one external host connected at any time.

2. Each network host in the camera array is called a node. Each node in the array generally has one or more camera sensors attached. Nodes may have additional sensors attached such as an IMU or GPS. There can be nodes with no camera. A node may also have a display or user interface. The configuration of sensors and devices available on a node is generally considered to be static for the duration of a boot cycle or collection session.

3. The goose is a node in the camera array which acts as the work coordinating interface to any external hosts. Goose is a role assigned to one node. When a host connects to the camera array it must determine which node is the goose. The role of goose may be assigned to a different node at different times and the host must update as needed. The other nodes are ducks.

## Communication

Messages from the external host can configure the array, start or stop collection, query for imagery, log additional data, and shutdown nodes in the array. The external host can subscribe for regular updates of some kinds of information. Communication with the external host is performed over GRPC.

Nodes in the camera array communicate with each other. Any communication specific to the function of gamma camera happens over a GRPC connection but the nodes also run other typical Linux services. Common services that are already available on Linux are favored over custom implementations - especially those that are not specific to the goal of collecting posed imagery. System logs are shared using syslog-ng. Network configuration happens via DHCP and DNS, etc.

All nodes in the array are connected to a single ethernet router in a star topology. External hosts communicate with the array by connecting to the same router or there may be a node which acts as a network bridge. If a node acts as a network bridge then it may be convenient or common for that device to be the coordinator but that's not required and should not be assumed. 