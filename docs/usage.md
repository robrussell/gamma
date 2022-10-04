# Folders and schema for working with the camera array

These directories either exist in the gamma repo or will be created during operation.

`jot/` - unversioned directory, good place to save recordings retrieved from the array

`notebooks/` - ipython notebooks

`ccline/` - camera control and logging

`deploy/` - software for setting up new nodes

`mechanical/` - 3d model source and STLs

Nodes have the directories:

`data/`

* `r_D/` - data for recording ID `r_D` from this node.
* `nocollection/` - data recorded with no active recording ID.

# Client commands

### Get a sample image from each node

The `sample` command captures a single frame from a single node. To get one image now from node `gamma1`, use:

```
./scripts/run.py --client --gin_configs prod.gin --cmd sample --target_node_id gamma1
```

This command runs the `CliRunner.camera_live_sample_cmd` on each camera node in sequence. When complete it moves all the resulting images to `jot/s_<datestamp>`

```
j="jot/s_$(date +%s)/" ; mkdir $j ; for s in {1..6} ; do ./scripts/run.py --client --gin_configs prod.gin --cmd sample --target_node_id gamma${s} ; done ; mv sample-*.jpg $j
```

### Collect imagery

Starting a collection will create a directory on each camera node at `data/r_<datestamp>` and save frames there.

```
./scripts/run.py --client --gin_configs prod.gin --cmd start
```

Issue the `stop` command to stop taking pictures.

```
./scripts/run.py --client --gin_configs prod.gin --cmd stop
```

On each node the Gamma camera server just runs the `CliRunner.camera_video_cmd` command from the supplied configuration file on that node. The provided configuration uses `libcamera-vid`.

# Hardware UI

A subset of the functions are available from a display with buttons attached to one of the camera array nodes. A collection can started or stopped and some stats can be viewed while collecting imagery. The UI delegates to the same client library, similar to the client commands above so that it's easy to turn any operation performed on the commandline into a menu action.

## Running ui.py at boot

The example systemd service `uiline.service` is provided. Install it on the node where the UI hardware is present. Once the service is enabled it will run `ui.py` when that Raspberry Pi boots up. When making changes to `ui.py` itself the service has to be stopped or restarted.

## Using the UI

When the ui is running with the OLED bonnet attached it shows a single menu item and a line of details relevant to that item. In general, pressing a button will activate the menu item which corresponds directly to running a Python function in ui.py. Since the code needs to be modified to suit the specifics of the camera array, it's best to read the code comments to get an idea of what the menu items actually do.

# Retrieving data

Use `rsync` to fetch data from one or all nodes. The `jot` directory is the intended location for data to land. Use a pattern like `r_collection-name`, for example `r_2022-09-01-hiking-trail`.

```
r=r_collection-name; mkdir jot/${r} ; for h in {1..6} ; do echo ${h} ; rsync pi@gamma${h}:data/${r}/*.jpg jot/${r}/gamma${h}/ ; done
```

### Retrieve imagery

The data from each node is stored on that node. Currently Gamma camera doesn't handle retrieving data from the array. The simplest way to to pull imagery from all nodes is probably `rsync`:

First find the name of the directory (it will be the same on all nodes):

```
ssh pi@gamma1 ls data/
```

The latest directory starting with `r_`, in this case it's r_1672602570. Run a command like this to copy files sequentially from each node to the workstation:

```
r=r_1672602570 ; mkdir jot/${r} ; for h in {1..6} ; do echo ${h} ; rsync pi@10.20.0.${h}:data/${r}/*.jpg jot/${r}/gamma${h}/ ; done
```