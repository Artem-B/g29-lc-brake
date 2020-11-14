# The MIT License (MIT)
#
# Copyright (c) 2018 Dan Halbert for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
`adafruit_hid.gamepad.Gamepad`
====================================================
* Author(s): Dan Halbert
"""

import struct
import time

from adafruit_hid import find_device


class Pedals:
    """ """

    def __init__(self, devices):
        """Create a Gamepad object that will send USB gamepad HID reports.
        Devices can be a list of devices that includes a gamepad device or a gamepad device
        itself. A device is any object that implements ``send_report()``, ``usage_page`` and
        ``usage``.
        """
        self._device = find_device(devices, usage_page=0x1, usage=0x04)

        # Reuse this bytearray to send reports.
        # 4 reports, 2-byte each = 8 bytes.
        self._report = bytearray(8)

        # Remember the last report as well, so we can avoid sending
        # duplicate reports.
        self._last_report = bytearray(8)

        # Store settings separately before putting into report. Saves code
        # especially for buttons.
        self._joy_x = 0
        self._joy_y = 0
        self._joy_z = 0
        self._joy_w = 0

        # Send an initial report to test if HID device is ready.
        # If not, wait a bit and try once more.
        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def set(self, x=None, y=None, z=None, w=None):
        """Set and send the given joystick values.
        The joysticks will remain set with the given values until changed
        One joystick provides ``x`` and ``y`` values,
        and the other provides ``z`` and ``r_z`` (z rotation).
        Any values left as ``None`` will not be changed.
        All values must be in the range -127 to 127 inclusive.
        Examples::
            # Change x and y values only.
            gp.move_joysticks(x=100, y=-50)
            # Reset all joystick values to center position.
            gp.move_joysticks(0, 0, 0, 0)
        """
        if x is not None:
            self._joy_x = self._validate_value(x)
        if y is not None:
            self._joy_y = self._validate_value(y)
        if z is not None:
            self._joy_z = self._validate_value(z)
        if w is not None:
            self._joy_w = self._validate_value(w)
        self._send()

    def reset_all(self):
        """Release all buttons and set joysticks to zero."""
        self._joy_x = 0
        self._joy_y = 0
        self._joy_z = 0
        self._joy_w = 0
        self._send(always=True)

    def _send(self, always=False):
        """Send a report with all the existing settings.
        If ``always`` is ``False`` (the default), send only if there have been changes.
        """
        struct.pack_into(
            "<hhhh",
            self._report,
            0,
            self._joy_x,
            self._joy_y,
            self._joy_z,
            self._joy_w,
        )

        if always or self._last_report != self._report:
            self._device.send_report(self._report)
            # Remember what we sent, without allocating new storage.
            self._last_report[:] = self._report

    @staticmethod
    def _validate_value(value):
        if not -32768 <= value <= 32767:
            raise ValueError("Out of range")
        return value
