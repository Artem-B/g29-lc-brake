# Logitech G29 pedals mod
- [Logitech G29 pedals mod](#logitech-g29-pedals-mod)
  - [What it does](#what-it-does)
  - [Why](#why)
  - [Required hardware](#required-hardware)
  - [Software](#software)
  - [Hardware -- the real hardware this time.](#hardware----the-real-hardware-this-time)

## What it does

- Adds load cell as the brake pressure sensor.
  - replaces lower part of the spring housing with a 3D-printed one.
- Adds Adafruit ItsyBitsy M4 express to process load cell data and
  potentiomenter readings as an independent (from the wheel) HID joystick with
  16-bit values. Un-invert the values reported by pedals while we're at that.

## Why

Humans easily adapt to control car braking by applying **pressure**. Logitech
pedals use potentiomenters that read pedal displacement. Relationship between
the applied pressure and the displacemmment is controlled by the brake's spring
with a rubber block intended to make the relationship non-linear. Unfortunately,
it squeezes whe wide range of high pressure values at the end of the pedal
travel into a rather narrow range of the pedal movement which logitech software then attempts to normalize into something more sensible.

It mostly works, but in practice I've found it rather hard to modulate the brake pressure precisely. One moment the car does not brake enough, then all of a sudden ABS goes nuts (or the car spins out). It just does not behave like a real car brake.

So, after eyeballing various higher-end pedals I've decided that I'm not *that*
interested in spending my toy budget on the ready-made gear. Instead, I've
figured that I can just mode the pedals using off-the shelf components.

TL; DR; It worked surprisingly well. Eventually.

## Required hardware

- Logitech G29/G920 pedals. The mod may work with G27 or other similar Logitech
  models, but you may need to tweak the spring housing model to fit.

- $15 [Adafruit ItsyBitsy M4 Express](https://www.adafruit.com/product/3800)
  
  It's amazing how much stuff you can cram into $15 worth of hardware:
  - ATSAMD51 32-bit Cortex M4 core running at 120 MHz
   
    You get a real 32-bit ARM processor, with tons of peripherals and you can
    program it in Python, if you want to. Why anyone is still using AVR-based
    overpriced and underpowered Arduino boards these days is beyond me.
  - Floating point support with Cortex M4 DSP instructions. -- M4 can do *a lot*
    of signal processing, if needed.
  - 512 KB flash, 192 KB RAM -- should be enough for everyone, right?
  - 2 MB SPI FLASH chip for storing files and CircuitPython code storage.

  Other thoughts

      About any chip with an USB interface, couple of GPIO pins for I2C and
      three ADC-capable inputs could do the job these days. `ItsyBitsy M4` is
      way overpowered for that and was largely chosen for convenience of writing
      software in Python.

      Surprisingly, not that many low-cost Cortex-M based boards have USB
      support. My usual go-to
      [`Discovery`](https://www.st.com/en/evaluation-tools/stm32-discovery-kits.html)
      and
      [`Nucleo`](https://www.st.com/en/evaluation-tools/stm32-nucleo-boards.html)
      boards from `STM` use USB for built-in STLink debugger and only pass
      through UART to the host.

      Trivia bit: $13
      [Nucleo-32](https://www.st.com/en/evaluation-tools/nucleo-g431kb.html)
      which is based on `stm32f431kb` uses `stm32f723` for the built-in ST-Link
      debugger. `F732` alone costs as much as the board and is much more capable
      than the `stm32f4` chip it debugs. How can one buy the whole board for
      less than the sum of the parts is a mystery to me. That said, I'm
      extremely happy with what $10-$15 can buy me in terms of tinkering
      supplies.


      ESP32 may be an interesting option for interfacing with the computer via Bluetooth, but that was considered to go beyond the `keep it simple` approach I was going for.

- $30 [FX29K0](https://www.te.com/usa-en/product-CAT-FSE0006.html?q=&d=581026%20644003&type=products&samples=N&inStoreWithoutPL=false&instock=N)
  100lbf/50kg load cell with I2C interface. 
  
  - Part number: FX29K0-100A-0100-L
  - [Datasheet](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FFX29%7FA3%7Fpdf%7FEnglish%7FENG_DS_FX29_A3.pdf%7F20009605-07) for FX29 load cells.
  - [Datasheet](https://www.idt.com/us/en/document/dst/zsc31014-datasheet) for `zsc31014` which is the measurement controller inside the FX29 load cell.

  There are quite a few variants of the load cell. You need the one starting
  with `FX29K` or `FX29J`, and ending with `0100-L` pr `0500-N`. If you use
  `FX29K`/`FX29J` followed by a digit other than `0`, you will need to adjust
  the I2C address in the `code.py`.

  The cell costs about $30 and is available from the usual sources.
  - [Digikey](https://www.digikey.com/en/products/detail/te-connectivity-measurement-specialties/FX29K0-100A-0100-L/11205661)
  - [Mouser](https://www.mouser.com/ProductDetail/Measurement-Specialties/FX29K0-100A-0100-L?qs=uwxL4vQweFMtAQMx%252BauT2Q%3D%3D)
  - [Others, via octopart.com](https://octopart.com/search?q=FX29K0-100A-0100-L&currency=USD&specs=0)

- Female DB-9 connector.
  
  Used to read the stock potentiomenter values via the reguler DB-9 connector from the pedals that normally plugs into the wheel base.

  I've repurposed an old serial cable I had in my `junk that may be useful one day` bin.

## Software

- [CircuitPython](https://circuitpython.readthedocs.io/en/6.0.x/README.html)
  
  That turned out to be the easiest way to get things working. I've considered
  multiple alternatives, but this method ended up winning based on the `results
  delivered`/`annoyance caused` ratio.

  - My [repo with the modified CirquitPython](https://github.com/Artem-B/circuitpython)

    The only changes are to ass `PEDALS` USB HID device for `ItsyBitsy M4 Express` board. If you want to use a different board, you'll need to make similar changes for that board.

  - Pedals software (this repo)
    
    Simple python script to read the values from `FX29` and the values of the stock potentiometers and report them via USB. Theb board also continually streams all the values over the serial port. It could be used to measure the relatinship between pedal displacement and the reported load. E.g. here are what my brake pedal reports depending on the spring setup:
    ![brake pedal load/displacement chart](https://user-images.githubusercontent.com/526795/100197993-0bade680-2eb0-11eb-973d-837f255e5410.png)
    

## Hardware -- the real hardware this time.

- Coins. I've used Euro 10c, [Danish 2
  kroner](https://en.wikipedia.org/wiki/Danish_krone) (yay for a center hole!)
  and an US 25c coins. You could probably use others, possibly filed down to
  size, or find appropriately sized washers.
- M4-0.7x20 screw + nut, but the size is not particularly critical, we just need
  a bump that will push on the load cell.

First mod version was prototyped using a bunch of schedule 40 PVC pipes and
couplers. It didn't quite work out. I had to build both upper and lower parts of
the spring housing. Making the parts telescoping into each other was hard to do
within the limited size choices and the constraints imposed by the pedal frame.
Without parts snugly fitting into each other, the spring buckles under the load
and the whole contraption flies apart. It turns out g29 pedal design uses a
number of subtle tricks to constrain spring housing motion to prevent spring
buckling. 