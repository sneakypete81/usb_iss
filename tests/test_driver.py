import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from hamcrest import assert_that, is_, calling, raises
from matchmock import called, called_once, called_once_with, not_called

from usb_iss import defs, UsbIssError
from usb_iss.driver import Driver

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray

# @TODO: Check for out of range data contents (0-255)


@patch('serial.Serial')
class TestDriver(unittest.TestCase):
    def test_open(self, serial):
        driver = Driver().open('PORTNAME')

        assert_that(serial, called())
        assert_that(driver._serial, is_(serial()))

    def test_close(self, serial):
        driver = Driver().open('PORTNAME')

        driver.close()

        assert_that(serial().close, called())
        assert_that(driver._serial, is_(None))

    def test_close_when_not_open(self, serial):
        driver = Driver().open('PORTNAME')

        driver.close()
        driver.close()

        assert_that(serial().close, called_once())
        assert_that(driver._serial, is_(None))

    def test_write_cmd_with_no_data(self, serial):
        driver = Driver().open('PORTNAME')

        driver.write_cmd(0x99)

        assert_that(serial().write, called_once_with(bytes([0x99])))

    def test_write_cmd_with_data(self, serial):
        driver = Driver().open('PORTNAME')

        driver.write_cmd(0x88, [0x01, 0x02])

        assert_that(serial().write, called_once_with(
            bytes([0x88, 0x01, 0x02])))

    def test_write_cmd_fails_when_not_open(self, _):
        driver = Driver()

        assert_that(
            calling(driver.write_cmd).with_args(0x99),
            raises(UsbIssError, "Serial port has not been opened"))

    def test_read(self, serial):
        driver = Driver().open('PORTNAME')
        serial().read.return_value = bytes([0x01, 0x02])

        data = driver.read(2)

        assert_that(data, is_([0x01, 0x02]))

    def test_read_zero_bytes(self, serial):
        driver = Driver().open('PORTNAME')

        data = driver.read(0)

        assert_that(data, is_([]))
        assert_that(serial().read.not_called())

    def test_read_failure(self, serial):
        driver = Driver().open('PORTNAME')
        serial().read.return_value = bytes([0x01, 0x02])

        assert_that(
            calling(driver.read).with_args(3),
            raises(UsbIssError, "Expected 3 bytes, but 2 received"))

    def test_read_fails_when_not_open(self, _):
        driver = Driver()

        assert_that(
            calling(driver.read).with_args(2),
            raises(UsbIssError, "Serial port has not been opened"))

    def test_check_ack_passing(self, serial):
        driver = Driver().open('PORTNAME')
        serial().read.return_value = bytes([0xFF])

        driver.check_ack()

    def test_check_ack_failing(self, serial):
        driver = Driver().open('PORTNAME')
        serial().read.return_value = bytes([0x00])

        assert_that(
            calling(driver.check_ack),
            raises(UsbIssError, "Received 0x00 instead of ACK"))

    def test_check_ack_error_code_passing(self, serial):
        driver = Driver().open('PORTNAME')
        serial().read.return_value = bytes([0xFF, 0x9A])

        result = driver.check_ack_error_code(defs.ModeError)

        assert_that(result, is_(0x9A))

    def test_check_ack_error_code_failing(self, serial):
        driver = Driver().open('PORTNAME')
        serial().read.return_value = bytes([0x00, 0x05])

        assert_that(
            calling(driver.check_ack_error_code).with_args(defs.ModeError),
            raises(UsbIssError, (r"Received ModeError.UNKNOWN_COMMAND " +
                                 r"\[0x00, 0x05\] instead of ACK")))
