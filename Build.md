# G29 brake mod build instructions.
- [G29 brake mod build instructions.](#g29-brake-mod-build-instructions)
  - [Software](#software)
    - [Build modified CircuitPython firmware](#build-modified-circuitpython-firmware)
    - [Update CircuitPython firmware](#update-circuitpython-firmware)
    - [Install required CircuitPython libraries](#install-required-circuitpython-libraries)
  - [Hardware](#hardware)
    - [Wiring](#wiring)
    - [3D print the spring holder](#3d-print-the-spring-holder)
    - [Assemble the mod](#assemble-the-mod)
    - [Mod the pedals.](#mod-the-pedals)
  - [Debugging](#debugging)

## Software

### Build modified CircuitPython firmware


Follow [CircuitPython build instructions](https://learn.adafruit.com/building-circuitpython/build-circuitpython) for `ItsyBitsy M4 Express`:

```shell
$ git clone https://github.com/Artem-B/circuitpython
$ cd circuitpython
$ git checkout main
$ git submodule sync --quiet --recursive
$ git submodule update --init
$ make -C mpy-cross
$ cd ports/atmel-samd
$ make BOARD=itsybitsy_m4_express
```

Once you're done you should have `build-itsybitsy_m4_express/firmware.uf2` file.

### Update CircuitPython firmware

Official Adafruit's [Firware upgrade instructions](https://learn.adafruit.com/introducing-adafruit-itsybitsy-m4/uf2-bootloader-details).

- double-click `reset` button on the ItsyBitsy board.
- you should see a new removable drive labeled `ITSYM4BOOT`
- copy `firmware.uf2` from the step above to that drive.

### Install required CircuitPython libraries

Once the firmware has been updated, you should see a new removable drive labeled
`CIRCUITPY`. That's where python files will go. 

- download the latest circuitpython library bundle from
  https://circuitpython.org/libraries and unpack it somewhere. Copy following
  files from the bundle into the `lib` directory on the `CIRCUITPY` drive:
  ```
  adafruit_hid/*
  simpleio.mpy
  ```
- copy all `.py` files from this repository into the root of the `CIRCUITPY` drive.

Software is ready to go now.


## Hardware

### Wiring

- I2C

    In order for I2C communication to work, you need to add two pull-up resistors -- one between `SCL` and `3.3V`, and one between `SDA` and `3.3V`.

- DB-9 for original pedal potentiomenters.

    Wire DB-9 Female connector pins to the following pins on `ItsyBitsy M4`:

    | DB-9 pin | `ItsyBitsy M4` pin | Purpose          |
    |----------|--------------------|------------------|
    |     1    | 3V                 | Reference voltage|
    |     2    | A0                 | Accelerometer pot|
    |     3    | A1                 | Brake pot        |
    |     4    | A2                 | Clutch pot       |
    |     6    | G                  | Signal Ground    |

- 4-pin connector for the load cell. 
  
  Wire connector pins for the load cell's signals:
    | load cell | `ItsyBitsy M4` pin |
    |-----------|--------------------|
    |  Red      | 3V. A5, if you want to change load cell parameters. |
    |  Yellow   | SCL                |
    |  White    | SDA                |
    |  Black    | G                  |

  I've used the standard 100mil header pins.

  The red wire supplies power to the load cell. In order to access the load
  cell's command mode, I2C command must be issued within 1.5-6ms of the cell power up. I've used a GPIO pin to supply the load cell's power. The cell's power consumption is below the 8mA that could be supplied by a GPIO pin on the `SAMD51G`. Powering the load cell from the 3.3V directly is fine for just reading the load cell measurements.


### 3D print the spring holder

3D print the model in [`CAD`](cad/README.md) subdirecory. I've printed it using
0.6mm nozzle and 0.4mm layer. You may need to file off the seams on the inside
and the outside of the printed part to ensure that the spring and the upper part
of the housing move smoothly.

### Assemble the mod

Attach the the washer to the bottom of the load cell using double-sided tape (it
must be about paper-thin, do not use thick foam tape) or some glue.

Thread the load cell cable through the hole in the side of the housing.

Place the load cell into the holder, with the load point bump facing upwards.

Drill a hole in a 25c coin, put a screw through it and fix it in position with a nut. The length of the screw should be short enough to fit under the white plastic cap in the original holder. Alternatively, you could place an appropriately sized stand-off on the screw and use that instead of the cap to guide/center the spring and serve as the support for the rubber insert, if you're planning to use one.

Place the coin & screw assembly into the housing, screw head down, so it contacts the load cell's center.

### Mod the pedals.

[Disassembly instructions](https://youtu.be/DxT2UOmHN-I?t=885) by `Sim Racing Garage` on YouTube.

- remove both parts of the spring housing.
- replace lower portion with the mod.
- Drill a hole in the upper part of the pedals' case and thread the load cell
  cable through.
- Drill two or four of holes on the back of the upper pedals shell and thread a
  zip-tie(s) through them. The zip ties will be used to mount the `ItsyBitsy M4`
  board.
- re-assemble the pedals.
- Connect the load call wires to the header you've soldered (or wire them to the
  `ItsyBitsy M4` directly)
- Plug in the original pedals connector to the female DB-9 you've wired above.
- Connect `ItsyBitsy M4` to the host via USB.

## Debugging

CircuitPython creates a virtual serial port. If/when something goes wrong, the normally-green LED on the `ItsyBitsy M4` will start flashing other colors. Connecting to the serial port will give you access to the Python REPL running on the board. When the mod app runs normally, it prints out every measured value for each of the potentiometers and for the load cell, so you can use it to verify that the pedals respond as intended.
