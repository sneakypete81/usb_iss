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


class TestIO(unittest.TestCase):
    def setUp(self):
        self.driver = Mock()
        self.io = IO(self.driver)

    def test_set_pins(self):
        self.io.set_pins(0, 1, 1, 1)

        assert_that(self.driver.write_cmd, called_once_with(0x63, [0x0E]))

    def test_set_pins_with_invalid_values(self):
        assert_that(
            calling(self.io.set_pins).with_args(0, 1, 1, 2),
            raises(UsbIssError))

    def test_set_pins_failure(self):
        self.driver.check_ack.side_effect = UsbIssError

        assert_that(
            calling(self.io.set_pins).with_args(0, 1, 1, 1),
            raises(UsbIssError))

    def test_get_pins(self):
        self.driver.read.return_value = [0x0E]

        data = self.io.get_pins()

        assert_that(self.driver.write_cmd, called_once_with(0x64))
        assert_that(self.driver.read, called_once_with(1))
        assert_that(data, is_([0, 1, 1, 1]))

    def test_get_ad(self):
        self.driver.read.return_value = [0x02, 0xA6]

        data = self.io.get_ad(1)

        assert_that(self.driver.write_cmd, called_once_with(0x65, [1]))
        assert_that(self.driver.read, called_once_with(2))
        assert_that(data, is_(0x02A6))
