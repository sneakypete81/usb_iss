import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from hamcrest import assert_that, is_, calling, raises
from matchmock import called_once_with, called_with

from usb_iss.serial_ import Serial
from usb_iss import UsbIssError


class TestSerial(unittest.TestCase):
    def setUp(self):
        self.driver = Mock()
        self.serial = Serial(self.driver)

    def test_transmit(self):
        self.serial.transmit([0x48, 0x65, 0x6c, 0x6c, 0x6f])

        assert_that(self.driver.write_cmd,
                    called_once_with(0x62, [0x48, 0x65, 0x6c, 0x6c, 0x6f]))

    def test_receive(self):
        self.driver.read.side_effect = [[0xFF, 0x1E, 0x02], [0x48, 0x69]]

        data = self.serial.receive()

        assert_that(data, is_([0x48, 0x69]))
        assert_that(self.driver.read, called_with(3))
        assert_that(self.driver.read, called_with(2))

    def test_receive_after_delay(self):
        self.driver.read.side_effect = [
            [0xFF, 0x1E, 0x00],
            [0xFF, 0x1E, 0x00],
            [0xFF, 0x1E, 0x02],
            [0x48, 0x69],
        ]

        data = self.serial.receive()

        assert_that(data, is_([0x48, 0x69]))
        assert_that(self.driver.read, called_with(3))
        assert_that(self.driver.read, called_with(2))

    def test_receive_error(self):
        self.driver.read.return_value = [0x00, 0x1E, 0x00]

        assert_that(calling(self.serial.receive),
                    raises(UsbIssError,
                           "NACK received - transmit buffer overflow"))

    def test_get_tx_count(self):
        self.driver.read.return_value = [0xFF, 0x1E, 0x00]

        tx_count = self.serial.get_tx_count()

        assert_that(tx_count, is_(30))
        assert_that(self.driver.read, called_once_with(3))

    def test_get_tx_count_error(self):
        self.driver.read.return_value = [0x00, 0x1E, 0x00]

        assert_that(calling(self.serial.get_tx_count),
                    raises(UsbIssError,
                           "NACK received - transmit buffer overflow"))

    def test_get_rx_count(self):
        self.driver.read.return_value = [0xFF, 0x1E, 0x00]

        rx_count = self.serial.get_rx_count()

        assert_that(rx_count, is_(0))
        assert_that(self.driver.read, called_once_with(3))

    def test_get_rx_count_error(self):
        self.driver.read.return_value = [0x00, 0x1E, 0x00]

        assert_that(calling(self.serial.get_rx_count),
                    raises(UsbIssError,
                           "NACK received - transmit buffer overflow"))
