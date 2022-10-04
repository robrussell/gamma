# Gamma P6 hardware

Gamma camera can be adapted to a wide variety of hardware. The most recently built prototype is gammacam P6. It has 6 camera nodes facing the same direction.

The Gamma camera P6 array consists of 6 nodes. 

## Per Node

* Raspberry Pi 4B
* microSD card
* MIPI CSI-2 to HDMI connector adapter

### Camera head

* Raspberry Pi HQ camera
* fisheye CS-mount lens
* ball head with 1/4"-20 thread
* 15mm Rod Clamp with 1/4"-20 thread

### Cables

* 2x Short FPC
  * one to connect Raspberry Pi CSI-2 to HDMI extension board
  * another to connect the HDMI extension board to the HQ camera
* HDMI cable
* ethernet cable
* USB-C right-angle power cable

## Router

* TP Link 1Gbps unmanaged hub
* USB to 9V power cable

## Rig

* 1x Adafruit 128x64 OLED Bonnet
* 6x 15mm rods, 20cm
* 4x 15mm railblock/rod clamp with 1/4"-20 thread
* M12 male to 1/4"-20 female screw adapter (for 15mm rod)
* 2x Grip handles with NATO quick release clamp
* 2x 15mm rod clamp with integrated NATO Rail
* 2x USB batteries (rated at 65W, 30,000mAh, 4 USB-A ports each)

## Printed parts

* one of camera-head.scad, camera-back.scad, and lens-cap.scad for each camera head
* one of rpi-bracket.scad for each Raspberry Pi
* two or more of tray.scad to hold up batteries and separate the Raspberry Pi boards from the metal router housing

## Screws, etc

* many M2.5 brass standoffs about 8mm-14mm to stack up the Raspberry Pi boards
* M2.5 nuts and screws for same
* M2.5 x 20mm machine screws to fasten HQ camera to printed parts
* M1 screws to fasten HDMI adapter boards to camera heads

# Camera rig description

The Gammacam P6 rig is split into two parts: the compute section and the camera sensor array. The compute section has two stacks of 3 Raspberry Pi 4B computers, the router, and two large USB batteries. The camera sensor array has 6 Raspberry Pi HQ camera sensors secured to 15mm rods with adjustable ball heads. Each camera head can be adjusted independently. Each Raspberry Pi HQ camera head is connected back to a Raspberry Pi 4B using an HDMI cable through appropriate adapter boards. The top Raspberry Pi 4B on one side has the OLED Bonnet installed to run the user interface.

Predecessors to Gammacam P6 attempted to use more 3d printed parts for the frame. However a wide variety of interoperable components built with 15mm rod and 1/4-20 mounting points make it simple to build custom camera applications. Current iterations mix these components with 3d printed parts. Using T-slot aluminum frames could also be a good option for other variations.

# Power

Two large batteries are sufficient to power the entire system for hours. The router used on Gammacam P6 isn't designed to be portable but the 9V power draw isn't very high so the USB to 9V barrel jack adapter is an easy solution.

# Hardware user interface

The camera array doesn't actually need any buttons or displays to operate. Most interactions are made to work using ssh from an external workstation. Local controls add a lot of flexibility though. The provided example user interface aims to help the operator know when the system is actually online and doing something. Change ui.py to suit the needs of the specific project. The code is designed to work well with a small OLED but a TFT or e-ink display with buttons wouldn't need much of a change. There's a small amount of hardware abstraction so for a fake UI for testing. This can be extended to operate in the terminal, simplifying the development cycle for a different display.

## Hardware UI alternative parts

The [Adafruit 128x64 OLED Bonnet for Raspberry Pi](https://www.adafruit.com/product/3531) is easy to work with. It's got two buttons, a joystick, and a monochrome OLED screen. The interface is I2C - it doesn't replicate an external HDMI display.

Adafruit makes a lot of other displays that fit on the Raspberry Pi header and has supported open source software for them for a long time. Here are some other good examples of displays that the ui code could be adapted for:

* [PiOLED - 128x32 Monochrome OLED](https://www.adafruit.com/product/3527)

Inexpensive but has no buttons, it could be used for displaying stats on a single node though.

* [2.13" Monochrome E-Ink Bonnet](https://www.adafruit.com/product/4687)

E-Ink is more visible than other options in bright light but the refresh rate is challenging.

* [Mini PiTFT 1.14" - 135x240 Color TFT](https://www.adafruit.com/product/4393)
* [Mini PiTFT 1.3" - 240x240 TFT](https://www.adafruit.com/product/4484)

The PiTFT devices and larger screens are more capable. The instructions with the device show it using a Linux kernel driver or directly over SPI through a Python library. The kernel driver is not needed, only the Python library.
