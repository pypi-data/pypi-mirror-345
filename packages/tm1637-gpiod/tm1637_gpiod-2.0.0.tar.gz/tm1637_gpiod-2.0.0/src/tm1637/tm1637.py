# Authored by: Asadullah Shaikh <github.com/pantheraleo-7>

import glob
import time

import gpiod
from gpiod.line import Direction, Value


__all__ = ["TM1637", "TM1637Decimal"]

TM1637_CMD1 = 0x40  # 0x40 data command
TM1637_CMD2 = 0xc0  # 0xC0 address command
TM1637_CMD3 = 0x80  # 0x80 display control command
TM1637_DELAY = 5e-6  # 5us delay between a pulse
TM1637_DSP_ON = 0x08  # 0x08 display on
TM1637_MSB = 0x80  # MSB is the decimal point or colon depending on the display

# 0-9, A-z, whitespace, hyphen, asterisk
_SEGMENTS = (
    b"\x3F\x06\x5B\x4F\x66\x6D\x7D\x07\x7F\x6F\x77\x7C\x39"
    b"\x5E\x79\x71\x3D\x76\x06\x1E\x76\x38\x55\x54\x3F\x73"
    b"\x67\x50\x6D\x78\x3E\x1C\x2A\x76\x6E\x5B\x00\x40\x63"
)


class TM1637:
    """Represents a TM1637 4-digit 7-segment LED display module."""

    def __init__(self, clk, dio, *, chip_path="/dev/gpiochip*", brightness=7):
        for path in glob.glob(chip_path):
            try:
                self._lines = gpiod.request_lines(
                    path,
                    consumer="tm1637",
                    config={(clk, dio): gpiod.LineSettings(direction=Direction.OUTPUT)},
                )
            except Exception:
                continue
            else:
                self.clk = clk
                self.dio = dio
                self.chip_path = path
                self.brightness = brightness
                break
        else:
            raise ValueError("No valid GPIO chip device found")

    def __del__(self):
        self._lines.release()

    def _start(self):
        self._lines.set_value(self.clk, Value.ACTIVE)
        self._lines.set_value(self.dio, Value.ACTIVE)
        self._lines.set_value(self.dio, Value.INACTIVE)
        self._lines.set_value(self.clk, Value.INACTIVE)

    def _stop(self):
        self._lines.set_value(self.clk, Value.INACTIVE)
        self._lines.set_value(self.dio, Value.INACTIVE)
        self._lines.set_value(self.clk, Value.ACTIVE)
        self._lines.set_value(self.dio, Value.ACTIVE)

    def _write_byte(self, byte):
        for i in range(8):
            self._lines.set_value(self.clk, Value.INACTIVE)
            self._lines.set_value(self.dio, Value((byte >> i) & 1))
            time.sleep(TM1637_DELAY)
            self._lines.set_value(self.clk, Value.ACTIVE)
            time.sleep(TM1637_DELAY)

        self._lines.set_value(self.clk, Value.INACTIVE)
        self._lines.set_value(self.clk, Value.ACTIVE)
        time.sleep(TM1637_DELAY)

    def _write_data_cmd(self):
        # automatic address increment, normal mode
        self._start()
        self._write_byte(TM1637_CMD1)
        self._stop()

    def _write_dsp_ctrl(self):
        # display on, set brightness
        self._start()
        self._write_byte(TM1637_CMD3 | TM1637_DSP_ON | self._brightness)
        self._stop()

    @property
    def brightness(self):
        """Get the display brightness."""
        return self._brightness

    @brightness.setter
    def brightness(self, val):
        """Set the display brightness, between 0-7."""
        if val not in range(8):
            raise ValueError(f"Brightness '{val}' is out of range")

        self._brightness = val
        self._write_data_cmd()
        self._write_dsp_ctrl()

    @staticmethod
    def encode_char(char):
        """Convert a character containing 0-9, A-z, whitespace, hyphen or asterisk
        to a segment."""
        o = ord(char)
        if o == 32:
            return _SEGMENTS[36]  # whitespace
        elif o == 42:
            return _SEGMENTS[38]  # asterisk
        elif o == 45:
            return _SEGMENTS[37]  # hyphen
        elif 48 <= o <= 57:
            return _SEGMENTS[o - 48]  # 0-9
        elif 65 <= o <= 90:
            return _SEGMENTS[o - 55]  # A-Z
        elif 97 <= o <= 122:
            return _SEGMENTS[o - 87]  # a-z
        else:
            raise ValueError(f"Character '{char}' ({o}) is out of range")

    @staticmethod
    def encode_digit(digit):
        """Convert a character containing 0-9 or a-f to a segment."""
        return _SEGMENTS[digit & 0x0f]

    @staticmethod
    def encode_string(string):
        """Convert a string containing 0-9, A-z, whitespace, hyphen or asterisk
        to an array of segments, matching the length of the source string."""
        segments = bytearray(len(string))
        for i, char in enumerate(string):
            segments[i] = TM1637.encode_char(char)
        return segments

    def write(self, segments, pos=0):
        """Display up to 4 segments, moving right from the specified position
        (default: 0)."""
        if pos not in range(4):
            raise ValueError(f"Position {pos} is out of range")

        self._write_data_cmd()
        self._start()
        self._write_byte(TM1637_CMD2 | pos)
        for seg in segments:
            self._write_byte(seg)
        self._stop()
        self._write_dsp_ctrl()

    def show(self, string, sep=False):
        """Display a string up to 4 characters long, left aligned.
        Optionally display a separator (default: False)."""
        string = "{:4s}".format(string)[:4]
        segments = self.encode_string(string)
        if sep:
            segments[1] |= TM1637_MSB
        self.write(segments)

    def scroll(self, string, delay=0.25):
        """Scroll a string across the display with the specified delay,
        given in seconds, between each step (default: 0.25)."""
        segments = b"\x00" * 4 + self.encode_string(string) + b"\x00" * 4
        for i in range(len(segments) - (4 - 1)):  # stop at right padding
            self.write(segments[i : i + 4])
            time.sleep(delay)

    def hex(self, val):
        """Display a hex value 0x0000 through 0xffff, right aligned."""
        string = "{:04x}".format(val & 0xffff)
        segments = self.encode_string(string)
        self.write(segments)

    def number(self, num):
        """Display an integer value -999 through 9999, right aligned."""
        num = max(-999, min(num, 9999))
        string = "{:4d}".format(num)
        segments = self.encode_string(string)
        self.write(segments)

    def numbers(self, num1, num2, sep=True):
        """Display two integer values -9 through 99, left zero padded.
        Optionally display a separator (default: True)."""
        num1 = max(-9, min(num1, 99))
        num2 = max(-9, min(num2, 99))
        string = "{:02d}{:02d}".format(num1, num2)
        segments = self.encode_string(string)
        if sep:
            segments[1] |= TM1637_MSB
        self.write(segments)

    def temperature(self, num):
        """Display a temperature integer value -9 through 99 with '*C' symbol.
        Values outside of this range show 'lo' for low or 'hi' for high."""
        if num < -9:
            self.show("lo")
        elif num > 99:
            self.show("hi")
        else:
            string = "{:2d}".format(num)
            segments = self.encode_string(string)
            self.write(segments)
        self.write([_SEGMENTS[38], _SEGMENTS[12]], pos=2)  # asterisk C

    def temperature_decimal(self, num):
        """Display a temperature decimal value -9.9 through 99.9 with '*' symbol.
        Values outside of this range show 'lo' for low or 'hi' for high."""
        if num < -9.9:
            self.show(" lo")
        elif num > 99.9:
            self.show(" hi")
        else:
            string = "{:4.1f}".format(num).replace(".", "")  # remove decimal point
            segments = self.encode_string(string)
            segments[1] |= TM1637_MSB
            self.write(segments)
        self.write([_SEGMENTS[38]], pos=3)  # asterisk


class TM1637Decimal(TM1637):
    """Represents a TM1637 4-digit 7-segment LED display module
    having a decimal point after each digit."""

    @staticmethod
    def encode_string(string):
        """Convert a string to LED segments.

        Convert a string containing 0-9, A-z, whitespace, hyphen, asterisk or period
        to an array of segments, matching the length of the source string."""
        segments = bytearray(len(string.replace(".", "")))  # remove decimal point(s)
        prev_char_period = True
        i = 0
        for char in string:
            if char == "." and not prev_char_period:
                segments[i - 1] |= TM1637_MSB
                prev_char_period = True
            else:
                segments[i] = TM1637.encode_char(char)
                prev_char_period = False
                i += 1
        return segments
