import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from hamcrest import assert_that, is_, calling, raises
from matchmock import called_once_with

from usb_iss.spi import SPI
from usb_iss import UsbIssError


class TestSPI(unittest.TestCase):
    def setUp(self):
        self.driver = Mock()
        self.spi = SPI(self.driver)

    def test_transfer(self):
        self.driver.read.return_value = [0x11, 0x22]

        result = self.spi.transfer([0x01, 0x41])

        assert_that(result, is_([0x11, 0x22]))
        assert_that(self.driver.write_cmd,
                    called_once_with(0x61, [0x01, 0x41]))
        assert_that(self.driver.read, called_once_with(2))

    def test_transfer_failure(self):
        self.driver.check_ack.side_effect = UsbIssError

        assert_that(
            calling(self.spi.transfer).with_args([0x01, 0x41]),
            raises(UsbIssError))

    def test_transfer_max_length(self):
        self.driver.read.return_value = list(range(62))

        result = self.spi.transfer(list(range(62)))

        assert_that(result, is_(list(range(62))))
        assert_that(self.driver.write_cmd,
                    called_once_with(0x61, list(range(62))))
        assert_that(self.driver.read, called_once_with(62))

    def test_transfer_too_long(self):

        assert_that(
            calling(self.spi.transfer).with_args(list(range(63))),
            raises(UsbIssError, "Attempted to write 63 bytes, maximum is 62"))
