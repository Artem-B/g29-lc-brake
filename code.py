import board
import time
import simpleio
import usb_hid
import math
import digitalio
import analogio
from struct import pack_into, unpack
import Pedals

def f(x):
    return int(32760*math.sin(float(x)/1000.0))

pedals = Pedals.Pedals(usb_hid.devices)

def pedal_sim():
    t = 0;
    while True:
        print("t=", t)
        pedals.set(x=f(t), y=f(t*2), z=f(t*3), w=f(t*4))
        t = t+1
        time.sleep(0.01)

def scan_i2c():
    i2c = board.I2C()
    
    while not i2c.try_lock():
        pass
    
    try:
        while True:
            print("I2C addresses found:", [hex(device_address)
                for device_address in i2c.scan()])
            time.sleep(2)
    
    finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
        i2c.unlock()    
        pass

class FX29:
    def __init__(self, addr=0x28, power_pin=board.A5):
        self._pwr = digitalio.DigitalInOut(power_pin)
        self._pwr.direction = digitalio.Direction.OUTPUT
        self.power(True)
        self._i2c = board.I2C()
        self._addr = addr
        self._buf = bytearray(4)
        self._i2c.unlock()
        while not self._i2c.try_lock():
            pass
        print("FX29 created")

    def power(self, on):
        self._pwr.value = on
        
    def read_mr(self):
        # Just read command & STOP
        self._i2c.readfrom_into(self._addr, self._buf, end = 0)

    @staticmethod
    def _sv(value):
        "Returns status/value tuple"
        s = value >> 14 & 0x3
        v = value & 0x3fff
        return s,v

    @staticmethod
    def _temp(value):
        "Returns temperature"
        t = value >> 5 & 0x3ff
        return t


    def read_mr2(self):
        # bridge data
        self._i2c.readfrom_into(self._addr, self._buf, end = 2)
        value, dummy = unpack('>HH', self._buf)
        s,v = self._sv(value)
        return s, v

    def read_mr4(self):
        # Bridge data & temperature
        self._i2c.readfrom_into(self._addr, self._buf)
        value, t = unpack('>HH', self._buf)
        s,v = self._sv(value)
        if s == 3:
            print("")
        return s, v, self._temp(t)


    def write_mr(self):
        # Write w/ no data
        self._i2c.writeto(self._addr, self._buf, end = 0)

    def enter_cmd_mode(self):
        self.power(False)
        time.sleep(0.01)
        self.power(True)
        time.sleep(0.003) # We have ~6 ms to enter command mode.
        self.cmd(0xA0)

    def exit_cmd_mode(self):
        self.cmd(0x80)
        time.sleep(0.02) # It may take up to 20ms to exit if we need to update EEPROM.
    
    def cmd(self, cmd, data=0):
        pack_into('>BHx', self._buf, 0, cmd, data)
        self._i2c.writeto(self._addr, self._buf, end=3)

    def read_eeprom(self, offset):
        if not 0 <= offset <= 0x13:
            return
        self.cmd(offset, 0)
        self._i2c.readfrom_into(self._addr, self._buf, end=3)
        ack, value = unpack('>BHx', self._buf)
        if ack != 0x5a:
            print("Got unexpected EEPROM read response:", hex(ack), hex(value))
            return
        return value

    def write_eeprom(self, offset, value):
        if not 0 <= offset <= 0x13:
            return
        v0 = self.read_eeprom(offset)
        # Write the new value
        self.cmd(0x40+offset, value)
        time.sleep(0.02) # EEPROM write takes up to 15ms
        v1 = self.read_eeprom(offset)
        print("W[%d]= %s:  %s -> %s" % (offset, hex(value), hex(v0), hex(v1)))

def adc_to_axis(v):
    return -32768 + (0xffff - v)

def load_to_axis(v):
    return int(-32768 + 3 * max(0, v-1000)) # Full span is 1000-15000, stretch it a bit.

def measure(fx29):
    accelerator_v = analogio.AnalogIn(board.A0)
    brake_v = analogio.AnalogIn(board.A1)
    clutch_v = analogio.AnalogIn(board.A2)
    last = time.monotonic_ns()
    last_report = last
    sent = 0
    t = 0
    while True:
        s, load = fx29.read_mr2()
        if s:
            continue
        brake = brake_v.value
        acc = accelerator_v.value
        clutch = clutch_v.value
        now = time.monotonic_ns()
        pedals.set(
            x=load_to_axis(load),
            y=adc_to_axis(brake),
            z=adc_to_axis(acc),
            w=adc_to_axis(clutch))
        sent += 1
        dt = (now - last ) // 1000
        last = now
        print(acc, brake, clutch, load, load_to_axis(load))
        last = now

def dump_eeprom(fx29):
    fx29.enter_cmd_mode()
    for i in range(0x13+1):
        v = fx29.read_eeprom(i)
        print(i, hex(v))
    fx29.exit_cmd_mode()

def disable_sleep(fx29):
    fx29.enter_cmd_mode()
    v = fx29.read_eeprom(1)
    if True or (v & 0x20):
        fx29.write_eeprom(1, 0x8001)
        v1 = fx29.read_eeprom(1)
        print("eeprom[1] : %s -> %s " % (hex(v), hex(v1)))
        fx29.exit_cmd_mode()
    fx29.exit_cmd_mode()


fx29 = FX29()
#dump_eeprom(fx29)
#disable_sleep(fx29)
#dump_eeprom(fx29)
#scan_i2c()
measure(fx29)
