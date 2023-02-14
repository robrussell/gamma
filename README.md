# Gamma Camera: a flexible camera array

Gamma camera provides an open source starting point to build a flexible camera array using commodity parts.

## Project Goals

Gamma camera attempts to raise the floor for researchers who need to collect multi-camera imagery. Cameras in the array may be used for stereo pairs but Gamma camera aims for a more flexible camera array rather than stereo. Researchers are encouraged to use Gamma Camera as a starting point to build camera rigs that suit their specific needs.

Some principles of the project:

* components should be "commercial off-the-shelf (COTS)" whenever possible
* rely on existing standards and norms whenever feasible
* encourage open source hardware and software
* reduce repetition of work unrelated to recording imagery and sensor data
* simplify reproduction of experimental setup
* develop with very recent releases of open source software

## What's included

Gamma Camera is primarily a software project with guidance on data storage but also includes reference material for building a suitable COTs multicamera array.

* Client and server software to start and stop collecting data
* Sample Python interaction with hardware UI, Jupyter notebook, and command line
* Bill of materials for a multicam rig
* 3d-printable part designs

## What's not included

Camera drivers, image processing, etc. This is handled by libcamera apps, OpenCV, or other mature software stacks.

Gamma camera explicitly tries not to introduce unnecessary constraints on users. The most visible result is that the gamma camera flexible camera array actually relies on existing camera drivers and image processing libraries to do most actual camera work.

## Getting started

The Hardware guide describes the camera rig currently used for development.

The Software guide describes how to install the software on a workstation and the camera array. It's also possible to simulate the software functionality by starting multiple gammacam nodes on one workstation. The simulation is generally intended for software development but it can be used to try out the system before committing to building the hardware.

The Usage guide explains general operations: starting and stopping the system, recording data, and retrieving data from the system.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

## Disclaimer

This project is not an official Google project. It is not supported by
Google and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.
