import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from hamcrest import assert_that, is_, calling, raises
from matchmock import called_once_with

from usb_iss.i2c import I2C, defs
from usb_iss.driver import Driver
from usb_iss import UsbIssError

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray

# @TODO: Check for out of range address/data (0-255)


class TestI2C(unittest.TestCase):
    def setUp(self):
        self.serial = Mock()
        driver = Driver()
        driver._serial = self.serial
        self.i2c = I2C(driver)

    def test_write(self):
        self.serial.read.return_value = bytes([0xFF])

        self.i2c.write(0xE0, 0x00, [0x51])

        assert_that(
            self.serial.write,
            called_once_with(bytes([0x55, 0xE0, 0x00, 0x01, 0x51])))

    def test_write_failure(self):
        self.serial.read.return_value = bytes([0x00])

        assert_that(
            calling(self.i2c.write).with_args(0xE0, 0x00, [0x51]),
            raises(UsbIssError, "Received NACK instead of ACK"))

    def test_write_large_data(self):
        self.serial.read.return_value = bytes([0xFF])
        expected_data = list(range(60))

        self.i2c.write(0xE0, 0x00, expected_data)

        assert_that(self.serial.write, called_once_with(bytes(
            [0x55, 0xE0, 0x00, 60] + expected_data)))

    def test_write_overflow_failure(self):
        self.serial.read.return_value = bytes([0xFF])
        expected_data = list(range(61))

        assert_that(
            calling(self.i2c.write).with_args(0xE0, 0x00, expected_data),
            raises(UsbIssError, "Attempted to write 61 bytes, maximum is 60"))

    def test_read(self):
        self.serial.read.return_value = bytes([0x11, 0x22])

        data = self.i2c.read(0xC1, 0x02, 2)

        assert_that(self.serial.write, called_once_with(
            bytes([0x55, 0xC1, 0x02, 2])))
        assert_that(data, is_([0x11, 0x22]))

    def test_read_failure(self):
        self.serial.read.return_value = bytes([0x11])

        assert_that(
            calling(self.i2c.read).with_args(0xC1, 0x02, 2),
            raises(UsbIssError, "Expected 2 bytes, but 1 received"))

    def test_read_large_data(self):
        expected_data = list(range(60))
        self.serial.read.return_value = bytes(expected_data)

        data = self.i2c.read(0xC1, 0x02, 60)

        assert_that(self.serial.write, called_once_with(
            bytes([0x55, 0xC1, 0x02, 60])))
        assert_that(data, is_(expected_data))

    def test_read_overflow_failure(self):

        assert_that(
            calling(self.i2c.read).with_args(0xC1, 0x02, 61),
            raises(UsbIssError, "Attempted to read 61 bytes, maximum is 60"))

    def test_write_single(self):
        self.serial.read.return_value = bytes([0xFF])

        self.i2c.write_single(0x40, 0x00)

        assert_that(self.serial.write, called_once_with(
            bytes([0x53, 0x40, 0x00])))

    def test_write_single_failure(self):
        self.serial.read.return_value = bytes([0x00])

        assert_that(
            calling(self.i2c.write_single).with_args(0x40, 0x00),
            raises(UsbIssError, "Received NACK instead of ACK"))

    def test_read_single(self):
        self.serial.read.return_value = bytes([0x42])

        data = self.i2c.read_single(0x41)

        assert_that(self.serial.write, called_once_with(bytes([0x53, 0x41])))
        assert_that(data, is_(0x42))

    def test_read_single_failure(self):
        self.serial.read.return_value = bytes([])

        assert_that(
            calling(self.i2c.read_single).with_args(0x41),
            raises(UsbIssError, "Expected 1 bytes, but 0 received"))

    def test_write_ad0(self):
        self.serial.read.return_value = bytes([0xFF])

        self.i2c.write_ad0(0x30, [0x12, 0x34, 0x56, 0x78])

        assert_that(self.serial.write, called_once_with(
            bytes([0x54, 0x30, 0x04, 0x12, 0x34, 0x56, 0x78])))

    def test_write_ad0_failure(self):
        self.serial.read.return_value = bytes([0x00])

        assert_that(
            calling(self.i2c.write_ad0).
            with_args(0x30, [0x12, 0x34, 0x56, 0x78]),
            raises(UsbIssError, "Received NACK instead of ACK"))

    def test_read_ad0(self):
        self.serial.read.return_value = bytes([0x11, 0x22])

        data = self.i2c.read_ad0(0xF1, 2)

        assert_that(self.serial.write, called_once_with(
            bytes([0x54, 0xF1, 2])))
        assert_that(data, is_([0x11, 0x22]))

    def test_read_ad0_failure(self):
        self.serial.read.return_value = bytes([0x11])

        assert_that(
            calling(self.i2c.read_ad0).with_args(0xF1, 2),
            raises(UsbIssError, "Expected 2 bytes, but 1 received"))

    def test_write_ad1(self):
        self.serial.read.return_value = bytes([0xFF])

        self.i2c.write_ad1(0xE0, 0x00, [0x51])

        assert_that(
            self.serial.write,
            called_once_with(bytes([0x55, 0xE0, 0x00, 0x01, 0x51])))

    def test_write_ad1_failure(self):
        self.serial.read.return_value = bytes([0x00])

        assert_that(
            calling(self.i2c.write_ad1).with_args(0xE0, 0x00, [0x51]),
            raises(UsbIssError, "Received NACK instead of ACK"))

    def test_write_ad1_large_data(self):
        self.serial.read.return_value = bytes([0xFF])
        expected_data = list(range(60))

        self.i2c.write_ad1(0xE0, 0x00, expected_data)

        assert_that(self.serial.write, called_once_with(bytes(
            [0x55, 0xE0, 0x00, 60] + expected_data)))

    def test_write_ad1_overflow_failure(self):
        self.serial.read.return_value = bytes([0xFF])
        expected_data = list(range(61))

        assert_that(
            calling(self.i2c.write_ad1).with_args(0xE0, 0x00, expected_data),
            raises(UsbIssError, "Attempted to write 61 bytes, maximum is 60"))

    def test_read_ad1(self):
        self.serial.read.return_value = bytes([0x11, 0x22])

        data = self.i2c.read_ad1(0xC1, 0x02, 2)

        assert_that(self.serial.write, called_once_with(
            bytes([0x55, 0xC1, 0x02, 2])))
        assert_that(data, is_([0x11, 0x22]))

    def test_read_ad1_failure(self):
        self.serial.read.return_value = bytes([0x11])

        assert_that(
            calling(self.i2c.read_ad1).with_args(0xC1, 0x02, 2),
            raises(UsbIssError, "Expected 2 bytes, but 1 received"))

    def test_read_ad1_large_data(self):
        expected_data = list(range(60))
        self.serial.read.return_value = bytes(expected_data)

        data = self.i2c.read_ad1(0xC1, 0x02, 60)

        assert_that(self.serial.write, called_once_with(
            bytes([0x55, 0xC1, 0x02, 60])))
        assert_that(data, is_(expected_data))

    def test_read_ad1_overflow_failure(self):

        assert_that(
            calling(self.i2c.read_ad1).with_args(0xC1, 0x02, 61),
            raises(UsbIssError, "Attempted to read 61 bytes, maximum is 60"))

    def test_write_ad2(self):
        self.serial.read.return_value = bytes([0xFF])

        self.i2c.write_ad2(0xA0, 0x1234, [0x51])

        assert_that(
            self.serial.write,
            called_once_with(bytes([0x56, 0xA0, 0x12, 0x34, 1, 0x51])))

    def test_write_ad2_failure(self):
        self.serial.read.return_value = bytes([0x00])

        assert_that(
            calling(self.i2c.write_ad2).with_args(0xA0, 0x1234, [0x51]),
            raises(UsbIssError, "Received NACK instead of ACK"))

    def test_write_ad2_large_data(self):
        self.serial.read.return_value = bytes([0xFF])
        expected_data = list(range(59))

        self.i2c.write_ad2(0xA0, 0x1234, expected_data)

        assert_that(self.serial.write, called_once_with(bytes(
            [0x56, 0xA0, 0x12, 0x34, 59] + expected_data)))

    def test_write_ad2_overflow_failure(self):
        self.serial.read.return_value = bytes([0xFF])
        expected_data = list(range(60))

        assert_that(
            calling(self.i2c.write_ad2).with_args(0xA0, 0x1234, expected_data),
            raises(UsbIssError, "Attempted to write 60 bytes, maximum is 59"))

    def test_read_ad2(self):
        self.serial.read.return_value = bytes([0x11, 0x22])

        data = self.i2c.read_ad2(0xA1, 0x4321, 2)

        assert_that(self.serial.write, called_once_with(
            bytes([0x56, 0xA1, 0x43, 0x21, 2])))
        assert_that(data, is_([0x11, 0x22]))

    def test_read_ad2_failure(self):
        self.serial.read.return_value = bytes([0x11])

        assert_that(
            calling(self.i2c.read_ad2).with_args(0xA1, 0x4321, 2),
            raises(UsbIssError, "Expected 2 bytes, but 1 received"))

    def test_read_ad2_large_data(self):
        expected_data = list(range(64))
        self.serial.read.return_value = bytes(expected_data)

        data = self.i2c.read_ad2(0xA1, 0x4321, 64)

        assert_that(self.serial.write, called_once_with(
            bytes([0x56, 0xA1, 0x43, 0x21, 64])))
        assert_that(data, is_(expected_data))

    def test_read_ad2_overflow_failure(self):

        assert_that(
            calling(self.i2c.read_ad2).with_args(0xC1, 0x02, 65),
            raises(UsbIssError, "Attempted to read 65 bytes, maximum is 64"))

    def test_direct(self):
        self.serial.read.side_effect = [
            bytes([0xFF, 4]),
            bytes([0x11, 0x22, 0x33, 0x44]),
            ]

        data = self.i2c.direct([
            defs.I2C_DIRECT_START,
            defs.I2C_DIRECT_WRITE3,
            0xA0, 0x00, 0x00,
            defs.I2C_DIRECT_RESTART,
            defs.I2C_DIRECT_WRITE1,
            0xA1,
            defs.I2C_DIRECT_READ4,
            defs.I2C_DIRECT_STOP,
            ])

        assert_that(self.serial.write, called_once_with(
            bytes([0x57, 0x01, 0x32, 0xA0, 0x00, 0x00, 0x02, 0x30, 0xA1, 0x23,
                   0x03])))
        assert_that(data, is_([0x11, 0x22, 0x33, 0x44]))

    def test_direct_failure(self):
        self.serial.read.return_value = bytes([0x00, 0x01])

        assert_that(
            calling(self.i2c.direct).with_args([
                defs.I2C_DIRECT_START,
                defs.I2C_DIRECT_WRITE3,
                0xA0, 0x00, 0x00,
                defs.I2C_DIRECT_RESTART,
                defs.I2C_DIRECT_WRITE1,
                0xA1,
                defs.I2C_DIRECT_READ4,
                defs.I2C_DIRECT_STOP,
                ]),
            raises(UsbIssError, r"Received \[0x00, 0x01\] instead of ACK"))

    def test_test_with_device(self):
        self.serial.read.return_value = bytes([0xFF])

        device_present = self.i2c.test(0xA0)

        assert_that(self.serial.write, called_once_with(bytes([0x58, 0xA0])))
        assert_that(device_present, is_(True))

    def test_test_without_device(self):
        self.serial.read.return_value = bytes([0x00])

        device_present = self.i2c.test(0xA0)

        assert_that(self.serial.write, called_once_with(bytes([0x58, 0xA0])))
        assert_that(device_present, is_(False))
