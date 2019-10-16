import unittest
from datetime import datetime, timedelta
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from hamcrest import assert_that, is_, greater_than, less_than, calling
from hamcrest import raises
from matchmock import called_once_with, called_with

from usb_iss.serial_ import Serial
from usb_iss import UsbIssError

EMPTY_READS = [[0xFF, 0x00, 0x00]] * 100


class TestSerial(unittest.TestCase):
    def setUp(self):
        self.driver = Mock()
        self.serial = Serial(self.driver)

        self.current_time = datetime(2000, 1, 1)

        def now_side_effect():
            self.current_time += timedelta(milliseconds=10)
            return self.current_time

        patcher = patch('usb_iss.serial_.datetime')
        self.addCleanup(patcher.stop)
        datetime_mock = patcher.start()
        datetime_mock.now.side_effect = now_side_effect

    def test_transmit(self):
        self.driver.read.side_effect = EMPTY_READS

        self.serial.transmit([0x48, 0x65, 0x6c, 0x6c, 0x6f])

        assert_that(self.driver.write_cmd,
                    called_once_with(0x62, [0x48, 0x65, 0x6c, 0x6c, 0x6f]))

    def test_receive(self):
        self.driver.read.side_effect = [[0xFF, 0x1E, 0x02],
                                        [0x48, 0x69]] + EMPTY_READS
        start_time = self.current_time

        data = self.serial.receive()

        assert_that(data, is_([0x48, 0x69]))
        assert_that(self.driver.read, called_with(3))
        assert_that(self.driver.read, called_with(2))

        elapsed_time = self.current_time - start_time
        assert_that(elapsed_time, greater_than(timedelta(milliseconds=100)))
        assert_that(elapsed_time, less_than(timedelta(milliseconds=200)))

    def test_receive_after_delay(self):
        self.driver.read.side_effect = [
            [0xFF, 0x1E, 0x00],
            [0xFF, 0x1E, 0x00],
            [0xFF, 0x1E, 0x02],
            [0x48, 0x69],
        ] + EMPTY_READS

        data = self.serial.receive()

        assert_that(data, is_([0x48, 0x69]))
        assert_that(self.driver.read, called_with(3))
        assert_that(self.driver.read, called_with(2))

    def test_receive_two_reads(self):
        self.driver.read.side_effect = [[0xFF, 0x1E, 0x02],
                                        [0x48, 0x69],
                                        [0xFF, 0x1E, 0x01],
                                        [0x32]] + EMPTY_READS
        start_time = self.current_time

        data = self.serial.receive()

        assert_that(data, is_([0x48, 0x69, 0x32]))
        assert_that(self.driver.read, called_with(3))
        assert_that(self.driver.read, called_with(2))
        assert_that(self.driver.read, called_with(1))

        elapsed_time = self.current_time - start_time
        assert_that(elapsed_time, greater_than(timedelta(milliseconds=100)))
        assert_that(elapsed_time, less_than(timedelta(milliseconds=200)))

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
        self.driver.read.side_effect = [[0xFF, 0x1E, 0x02], [0x48, 0x69]]

        rx_count = self.serial.get_rx_count()

        assert_that(rx_count, is_(2))
        assert_that(self.driver.read, called_with(3))
        assert_that(self.driver.read, called_with(2))

    def test_get_rx_count_error(self):
        self.driver.read.return_value = [0x00, 0x1E, 0x00]

        assert_that(calling(self.serial.get_rx_count),
                    raises(UsbIssError,
                           "NACK received - transmit buffer overflow"))
