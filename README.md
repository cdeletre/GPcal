# GPcal
A gamepad calibration tool for the Retroid Pocket 5 and Mini

![image](https://raw.githubusercontent.com/cdeletre/GPcal/main/pics/screenshot.jpg)

## Installation

The actual version of the tool uses the PortMaster running environment. It needs to be installed in the `ports` directory.

You also need to use a special build of the kernel for the moment as the patch of the kernel driver is not available yet in the CFW.

## Running

Start the tool from the Ports list.

## Controls
|Button|Action|
|--|--|
|DPAD|select a button/control|
|A|OK|
|B|Cancel/Back|

## How to calibrate ?

Choose Calibrate and select a control you want to calibrate, then follow the instructions.

## How to cancel a calibration in progress ?

Just press B

## How to reset the calibration parameters ?

Use the Reset button

## How to save the calibration parameters ?

Use the Save button. A bash script will be written in the HOME directory. Run this script to restore the parameters.

## How to exit ?

Use the Quit button.

# Are the calibration parameters permanently modified ?

No, they'll be restored to default after a reboot. If you want them permanent you can run the bash script on each boot.

## What is SDL view ?

This tool calibrates the raw value of the controller which have an unfixed and undetermined range of values that depends on the hardware and the calibration applied (center, deadzone, antideadzone). An SDL gamepad controller uses fixed ranges of value (typically -32768 to 32767), which are calculated from the raw value and the calibration parameters. When you enable the SDL view the position on stick and trigger visuals are calculated like SDL would do, typically the stick can not go ouside of the limit.