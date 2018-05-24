import unittest
# Py2 doesn't have mock included in unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from hamcrest import assert_that, is_, calling, raises
from matchmock import called_with, called_once_with

from usb_iss import UsbIss, UsbIssError, defs



class TestUSbIss(unittest.TestCase):
    def setUp(self):
        self.usb_iss = UsbIss()
        self.driver = Mock()
        self.usb_iss._drv = self.driver

    def test_open(self):
        self.usb_iss.open('PORTNAME')

        assert_that(self.driver.open, called_once_with('PORTNAME'))

    def test_setup_i2c(self):
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
                io2_type=defs.IOType.OUTPUT_HIGH)

            assert_that(self.driver.write_cmd,
                        called_with(0x5A, [0x02, i2c_mode, 0x04]))

    def test_setup_i2c_default_values(self):
        self.usb_iss.setup_i2c()

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [
                        0x02,
                        defs.Mode.I2C_H_400KHZ.value,
                        defs.IOType.DIGITAL_INPUT.value << 2 |
                        defs.IOType.DIGITAL_INPUT.value]))

    def test_setup_i2c_failure(self):
        self.driver.check_ack_error_code.side_effect = UsbIssError

        assert_that(calling(self.usb_iss.setup_i2c),
                    raises(UsbIssError))
        assert_that(self.driver.check_ack_error_code,
                    called_once_with(defs.ModeError))

    def test_setup_i2c_serial(self):
        test_matrix = [
            (20, False, 0x21),
            (50, False, 0x31),
            (100, False, 0x41),
            (400, False, 0x51),
            (100, True, 0x61),
            (400, True, 0x71),
            (1000, True, 0x81),
        ]

        for (clk_khz, use_i2c_hardware, i2c_mode) in test_matrix:
            self.usb_iss.setup_i2c_serial(
                clock_khz=clk_khz,
                use_i2c_hardware=use_i2c_hardware)

            assert_that(self.driver.write_cmd,
                        called_with(0x5A, [0x02, i2c_mode, 0x01, 0x37]))

    def test_setup_i2c_serial_baud_rates(self):
        test_matrix = [
            (300, [0x27, 0x0F]),
            (1200, [0x09, 0xC3]),
            (2400, [0x04, 0xE1]),
            (9600, [0x01, 0x37]),
            (19200, [0x00, 0x9B]),
            (38400, [0x00, 0x4D]),
            (57600, [0x00, 0x33]),
            (115200, [0x00, 0x19]),
        ]

        for (baud_rate, divisor) in test_matrix:
            self.usb_iss.setup_i2c_serial(baud_rate=baud_rate)

            assert_that(self.driver.write_cmd,
                        called_with(0x5A, [
                            0x02,
                            defs.Mode.I2C_H_400KHZ.value | 0x01] +
                            divisor))

    def test_setup_i2c_serial_default_values(self):
        self.usb_iss.setup_i2c_serial()

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [
                        0x02,
                        defs.Mode.I2C_H_400KHZ.value | 0x01,
                        0x01,
                        0x37]))

    def test_setup_i2c_serial_overflow(self):
        self.usb_iss.setup_i2c_serial(baud_rate=1)

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [
                        0x02,
                        defs.Mode.I2C_H_400KHZ.value | 0x01,
                        0xFF,
                        0xFF]))

    def test_setup_i2c_serial_failure(self):
        self.driver.check_ack_error_code.side_effect = UsbIssError

        assert_that(calling(self.usb_iss.setup_i2c_serial),
                    raises(UsbIssError))
        assert_that(self.driver.check_ack_error_code,
                    called_once_with(defs.ModeError))

    def test_setup_spi(self):
        test_matrix = [
            (3000, 1),
            (500, 11),
            (23, 255),
        ]

        for (clk_khz, divisor) in test_matrix:
            self.usb_iss.setup_spi(
                spi_mode=defs.SPIMode.TX_IDLE_TO_ACTIVE_IDLE_HIGH,
                clock_khz=clk_khz)

            assert_that(self.driver.write_cmd,
                        called_with(0x5A, [0x02, 0x93, divisor]))

    def test_setup_spi_default_values(self):
        self.usb_iss.setup_spi()

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [0x02, 0x90, 11]))

    def test_setup_spi_overflow(self):
        self.usb_iss.setup_spi(clock_khz=1)

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [0x02, 0x90, 0xFF]))

    def test_setup_spi_failure(self):
        self.driver.check_ack_error_code.side_effect = UsbIssError

        assert_that(calling(self.usb_iss.setup_spi),
                    raises(UsbIssError))
        assert_that(self.driver.check_ack_error_code,
                    called_once_with(defs.ModeError))

    def test_setup_io(self):
        self.usb_iss.setup_io(
            io1_type=defs.IOType.OUTPUT_LOW,
            io2_type=defs.IOType.OUTPUT_HIGH,
            io3_type=defs.IOType.ANALOGUE_INPUT,
            io4_type=defs.IOType.DIGITAL_INPUT)

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [0x02, 0x00, 0xB4]))

    def test_setup_io_default_values(self):
        self.usb_iss.setup_io()

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [
                        0x02,
                        0x00,
                        defs.IOType.DIGITAL_INPUT.value << 6 |
                        defs.IOType.DIGITAL_INPUT.value << 4 |
                        defs.IOType.DIGITAL_INPUT.value << 2 |
                        defs.IOType.DIGITAL_INPUT.value]))

    def test_setup_io_failure(self):
        self.driver.check_ack_error_code.side_effect = UsbIssError

        assert_that(calling(self.usb_iss.setup_io),
                    raises(UsbIssError))
        assert_that(self.driver.check_ack_error_code,
                    called_once_with(defs.ModeError))

    def test_change_io(self):
        self.usb_iss.change_io(
            io1_type=defs.IOType.OUTPUT_LOW,
            io2_type=defs.IOType.OUTPUT_HIGH,
            io3_type=defs.IOType.ANALOGUE_INPUT,
            io4_type=defs.IOType.DIGITAL_INPUT)

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [0x02, 0x10, 0xB4]))

    def test_change_io_default_values(self):
        self.usb_iss.change_io()

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A, [
                        0x02,
                        0x10,
                        defs.IOType.DIGITAL_INPUT.value << 6 |
                        defs.IOType.DIGITAL_INPUT.value << 4 |
                        defs.IOType.DIGITAL_INPUT.value << 2 |
                        defs.IOType.DIGITAL_INPUT.value]))

    def test_change_io_failure(self):
        self.driver.check_ack_error_code.side_effect = UsbIssError

        assert_that(calling(self.usb_iss.change_io),
                    raises(UsbIssError))
        assert_that(self.driver.check_ack_error_code,
                    called_once_with(defs.ModeError))

    def test_setup_serial_baud_rates(self):
        test_matrix = [
            (300, [0x27, 0x0F]),
            (1200, [0x09, 0xC3]),
            (2400, [0x04, 0xE1]),
            (9600, [0x01, 0x37]),
            (19200, [0x00, 0x9B]),
            (38400, [0x00, 0x4D]),
            (57600, [0x00, 0x33]),
            (115200, [0x00, 0x19]),
        ]

        for (baud_rate, divisor) in test_matrix:
            self.usb_iss.setup_serial(baud_rate=baud_rate,
                                      io3_type=defs.IOType.OUTPUT_LOW,
                                      io4_type=defs.IOType.OUTPUT_HIGH)

            assert_that(self.driver.write_cmd,
                        called_with(0x5A, [0x02, 0x01] + divisor + [0x40]))

    def test_setup_serial_default_values(self):
        self.usb_iss.setup_serial()

        assert_that(self.driver.write_cmd,
                    called_once_with(0x5A,
                                     [0x02, 0x01, 0x01, 0x37,
                                      defs.IOType.DIGITAL_INPUT.value << 6 |
                                      defs.IOType.DIGITAL_INPUT.value << 4]))

    def test_setup_serial_failure(self):
        self.driver.check_ack_error_code.side_effect = UsbIssError

        assert_that(calling(self.usb_iss.setup_serial),
                    raises(UsbIssError))
        assert_that(self.driver.check_ack_error_code,
                    called_once_with(defs.ModeError))

    def test_read_module_id(self):
        self.driver.read.return_value = [0x07, 0x02, 0x40]

        result = self.usb_iss.read_module_id()

        assert_that(result, is_(0x07))
        assert_that(self.driver.write_cmd, called_once_with(0x5A, [0x01]))
        assert_that(self.driver.read, called_once_with(3))

    def test_read_fw_version(self):
        self.driver.read.return_value = [0x07, 0x02, 0x40]

        result = self.usb_iss.read_fw_version()

        assert_that(result, is_(0x02))
        assert_that(self.driver.write_cmd, called_once_with(0x5A, [0x01]))
        assert_that(self.driver.read, called_once_with(3))

    def test_read_iss_mode(self):
        self.driver.read.return_value = [0x07, 0x02, 0x40]

        result = self.usb_iss.read_iss_mode()

        assert_that(result, is_(defs.Mode.I2C_S_100KHZ))
        assert_that(self.driver.write_cmd, called_once_with(0x5A, [0x01]))
        assert_that(self.driver.read, called_once_with(3))

    def test_read_serial_number(self):
        self.driver.read.return_value = [
            0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x31]

        result = self.usb_iss.read_serial_number()

        assert_that(result, is_("00000001"))
        assert_that(self.driver.write_cmd, called_once_with(0x5A, [0x03]))
        assert_that(self.driver.read, called_once_with(8))
