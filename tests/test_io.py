import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from hamcrest import assert_that, is_, calling, raises
from matchmock import called_once_with

from usb_iss import UsbIssError
from usb_iss.io import IO
from usb_iss.driver import Driver

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray

# @TODO: Check for pin values >1


class TestIO(unittest.TestCase):
    def setUp(self):
        self.serial = Mock()
        driver = Driver()
        driver._serial = self.serial
        self.io = IO(driver)

    def test_set_pins(self):
        self.serial.read.return_value = bytes([0xFF])

        self.io.set_pins(0, 1, 1, 1)

        assert_that(self.serial.write, called_once_with(bytes([0x63, 0x0E])))

    def test_set_pins_failure(self):
        self.serial.read.return_value = bytes([0x00])

        assert_that(
            calling(self.io.set_pins).with_args(0, 1, 1, 1),
            raises(UsbIssError, "Received 0x00 instead of ACK"))

    def test_get_pins(self):
        self.serial.read.return_value = bytes([0x0E])

        data = self.io.get_pins()

        assert_that(self.serial.write, called_once_with(bytes([0x64])))
        assert_that(data, is_([0, 1, 1, 1]))

    def test_get_ad(self):
        self.serial.read.return_value = bytes([0x02, 0xA6])

        data = self.io.get_ad(1)

        assert_that(self.serial.write, called_once_with(bytes([0x65, 1])))
        assert_that(data, is_(0x02A6))
