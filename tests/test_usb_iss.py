import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from hamcrest import assert_that, is_, calling, raises
from matchmock import called, called_with, called_once_with

from usb_iss import UsbIss, UsbIssError, defs

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray


class TestUSbIss(unittest.TestCase):
    def setUp(self):
        self.serial = Mock()
        self.usb_iss = UsbIss()
        self.usb_iss._drv._serial = self.serial

    @patch('serial.Serial')
    def test_open(self, serial):
        UsbIss().open('PORTNAME')

        assert_that(serial, called())

    def test_setup_i2c(self):
        self.serial.read.return_value = bytes([0xFF, 0x00])
        test_matrix = [
            (20, False, 0x20),
            (50, False, 0x30),
            (100, False, 0x40),
            (400, False, 0x50),
            (100, True, 0x60),
            (400, True, 0x70),
            (1000, True, 0x80),
        ]

        for (clk_khz, use_i2c_hardware, i2c_mode) in test_matrix:
            self.usb_iss.setup_i2c(
                clock_khz=clk_khz,
                use_i2c_hardware=use_i2c_hardware,
                io1_type=defs.IOType.OUTPUT_LOW,
                io2_type=defs.IOType.OUTPUT_HIGH,
            )

            assert_that(self.serial.write, called_with(
                bytes([0x5A, 0x02, i2c_mode, 0x04])))

    def test_setup_i2c_default_values(self):
        self.serial.read.return_value = bytes([0xFF, 0x00])
        self.usb_iss.setup_i2c()

        assert_that(self.serial.write, called_with(
            bytes([0x5A, 0x02, defs.Mode.I2C_H_400KHZ.value,
                   defs.IOType.DIGITAL_INPUT.value << 2 |
                   defs.IOType.DIGITAL_INPUT.value])))

    def test_setup_i2c_failure(self):
        self.serial.read.return_value = bytes([0x00, 0x05])

        assert_that(
            calling(self.usb_iss.setup_i2c).with_args(
                clock_khz=100,
                use_i2c_hardware=True,
                io1_type=defs.IOType.OUTPUT_LOW,
                io2_type=defs.IOType.OUTPUT_HIGH),
            raises(UsbIssError, (r"Received ModeError.UNKNOWN_COMMAND " +
                                 r"\[0x00, 0x05\] instead of ACK")))

    def test_read_module_id(self):
        self.serial.read.return_value = bytes([0x07, 0x02, 0x40])

        result = self.usb_iss.read_module_id()

        assert_that(result, is_(0x07))
        assert_that(self.serial.write, called_once_with(bytes([0x5A, 0x01])))

    def test_read_fw_version(self):
        self.serial.read.return_value = bytes([0x07, 0x02, 0x40])

        result = self.usb_iss.read_fw_version()

        assert_that(result, is_(0x02))
        assert_that(self.serial.write, called_once_with(bytes([0x5A, 0x01])))

    def test_read_iss_mode(self):
        self.serial.read.return_value = bytes([0x07, 0x02, 0x40])

        result = self.usb_iss.read_iss_mode()

        assert_that(result, is_(defs.Mode.I2C_S_100KHZ))
        assert_that(self.serial.write, called_once_with(bytes([0x5A, 0x01])))

    def test_read_serial_number(self):
        self.serial.read.return_value = bytes(
            [0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x31])

        result = self.usb_iss.read_serial_number()

        assert_that(result, is_("00000001"))
        assert_that(self.serial.write, called_once_with(bytes([0x5A, 0x03])))
