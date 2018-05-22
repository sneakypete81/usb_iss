from . import defs
from .exceptions import UsbIssError
from .driver import Driver, DummyDriver
from .i2c import I2C
from .io import IO

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray


class UsbIss(object):
    """
    Main USB_ISS object.

    Example:
        ::

            from usb_iss import UsbIss, defs

            # Configure I2C mode

            iss = UsbIss()
            iss.open("COM3")
            iss.setup_i2c()

            # Write and read back some data

            iss.i2c.write(0xC4, 0, [0, 1, 2]);
            data = iss.i2c.read(0xC4, 0, 3)

            print(data)
            # [0, 1, 2]

    Attributes:
        i2c (:class:`i2c.I2C`): Attribute to use for I2C access.
        io (:class:`io.IO`): Attribute to use for pin IO access.

    """
    def __init__(self, dummy=False):
        self._drv = DummyDriver() if dummy else Driver()

        self.i2c = I2C(self._drv)
        self.io = IO(self._drv)

    def open(self, port):
        """
        Open the specified serial port for communication with the USB_ISS
        module.

        Args:
            port (str): Serial port to use for usb_iss communication.
        """
        self._drv.open(port)
        return self

    def close(self):
        """
        Close the serial port.
        """
        self._drv.close()

    def setup_i2c(self, clock_khz=400, use_i2c_hardware=True,
                  io1_type=defs.IOType.DIGITAL_INPUT,
                  io2_type=defs.IOType.DIGITAL_INPUT):
        """
        Issue a ISS_MODE command to set the operating mode to I2C + IO.

        Args:
            clock_khz (int): I2C clock rate in kHz.
                See https://www.robot-electronics.co.uk/htm/usb_iss_tech.htm
                for a list of valid values.
            use_i2c_hardware (bool): Use the USB_ISS module's hardware I2C
                controller.
            io1_type (defs.IOType): IO1 mode
            io2_type (defs.IOType): IO2 mode
        """
        i2c_mode = self._get_i2c_mode(clock_khz, use_i2c_hardware)
        io_type = self._get_io_type(io1_type, io2_type,
                                    defs.IOType.NULL, defs.IOType.NULL)
        self._set_mode(i2c_mode, [io_type])

    def setup_i2c_serial(self, clock_khz=400, use_i2c_hardware=True,
                         baud_rate=9600):
        """
        Issue a ISS_MODE command to set the operating mode to I2C + Serial.

        Args:
            clock_khz (int): I2C clock rate in kHz.
                See https://www.robot-electronics.co.uk/htm/usb_iss_tech.htm
                for a list of valid values.
            use_i2c_hardware (bool): Use the USB_ISS module's hardware I2C
                controller.
            baud_rate (int): Baud rate for the serial interface.
        """
        i2c_mode = self._get_i2c_mode(clock_khz, use_i2c_hardware)
        divisor = self._get_serial_divisor(baud_rate)
        self._set_mode(i2c_mode | defs.Mode.SERIAL.value, divisor)

    def setup_spi(self, spi_mode=defs.SPIMode.TX_ACTIVE_TO_IDLE_IDLE_LOW,
                  clock_khz=500):
        """
        Issue a ISS_MODE command to set the operating mode to SPI.

        Args:
            spi_mode (defs.SPIMode): SPI mode option to use.
            clock_khz (int): SPI clock rate in kHz.
        """
        divisor = self._get_spi_divisor(clock_khz)
        self._set_mode(spi_mode.value, [divisor])

    def setup_io(self,
                 io1_type=defs.IOType.DIGITAL_INPUT,
                 io2_type=defs.IOType.DIGITAL_INPUT,
                 io3_type=defs.IOType.DIGITAL_INPUT,
                 io4_type=defs.IOType.DIGITAL_INPUT):
        """
        Issue a ISS_MODE command to set the operating mode to IO.

        Args:
            io1_type (defs.IOType): IO1 mode
            io2_type (defs.IOType): IO2 mode
            io3_type (defs.IOType): IO3 mode
            io4_type (defs.IOType): IO4 mode
        """
        io_type = self._get_io_type(io1_type, io2_type, io3_type, io4_type)
        self._set_mode(defs.Mode.IO_MODE.value, [io_type])

    def change_io(self,
                  io1_type=defs.IOType.DIGITAL_INPUT,
                  io2_type=defs.IOType.DIGITAL_INPUT,
                  io3_type=defs.IOType.DIGITAL_INPUT,
                  io4_type=defs.IOType.DIGITAL_INPUT):
        """
        Issue a ISS_MODE command to change the current IO mode without
        affecting serial or I2C settings.

        Args:
            io1_type (defs.IOType): IO1 mode
            io2_type (defs.IOType): IO2 mode
            io3_type (defs.IOType): IO3 mode
            io4_type (defs.IOType): IO4 mode
        """
        io_type = self._get_io_type(io1_type, io2_type, io3_type, io4_type)
        self._set_mode(defs.Mode.IO_CHANGE.value, [io_type])

    def setup_serial(self, baud_rate=9600,
                     io3_type=defs.IOType.DIGITAL_INPUT,
                     io4_type=defs.IOType.DIGITAL_INPUT):
        """
        Issue a ISS_MODE command to set the operating mode to Serial + IO.

        Args:
            baud_rate (int): Baud rate for the serial interface.
            io3_type (defs.IOType): IO3 mode
            io4_type (defs.IOType): IO4 mode
        """
        divisor = self._get_serial_divisor(baud_rate)
        io_type = self._get_io_type(defs.IOType.NULL, defs.IOType.NULL,
                                    io3_type, io4_type)
        self._set_mode(defs.Mode.IO.value | defs.Mode.SERIAL.value,
                       divisor + [io_type])

    def read_module_id(self):
        """
        Returns:
            int: The USB_ISS module ID (always 7).
        """
        self._drv.write_cmd(defs.CMD_USB_ISS,
                            [defs.SubCommand.ISS_VERSION.value])
        return self._drv.read(3)[0]

    def read_fw_version(self):
        """
        Returns:
            int: The USB_ISS firmware version.
        """
        self._drv.write_cmd(defs.CMD_USB_ISS,
                            [defs.SubCommand.ISS_VERSION.value])
        return self._drv.read(3)[1]

    def read_iss_mode(self):
        """
        Returns:
            defs.Mode: The current ISS_MODE operating mode.
        """
        self._drv.write_cmd(defs.CMD_USB_ISS,
                            [defs.SubCommand.ISS_VERSION.value])
        return defs.Mode(self._drv.read(3)[2])

    def read_serial_number(self):
        """
        Returns:
            str: The serial number of the attached USB_ISS module.
        """
        self._drv.write_cmd(defs.CMD_USB_ISS,
                            [defs.SubCommand.GET_SER_NUM.value])
        return bytes(self._drv.read(8)).decode('ascii')

    def _set_mode(self, mode_value, data):
        data = [defs.SubCommand.ISS_MODE.value, mode_value] + data
        self._drv.write_cmd(defs.CMD_USB_ISS, data)
        self._drv.check_ack_error_code(defs.ModeError)

    @staticmethod
    def _get_io_type(io1_type, io2_type, io3_type, io4_type):
        return ((io1_type.value << 0) | (io2_type.value << 2) |
                (io3_type.value << 4) | (io4_type.value << 6))

    @staticmethod
    def _get_i2c_mode(clock_khz, use_i2c_hardware):
        if clock_khz == 20:
            assert not use_i2c_hardware
            return defs.Mode.I2C_S_20KHZ.value
        if clock_khz == 50:
            assert not use_i2c_hardware
            return defs.Mode.I2C_S_50KHZ.value
        if clock_khz == 100:
            return (defs.Mode.I2C_H_100KHZ.value if use_i2c_hardware else
                    defs.Mode.I2C_S_100KHZ.value)
        if clock_khz == 400:
            return (defs.Mode.I2C_H_400KHZ.value if use_i2c_hardware else
                    defs.Mode.I2C_S_400KHZ.value)
        if clock_khz == 1000:
            assert use_i2c_hardware
            return defs.Mode.I2C_H_1000KHZ.value

        raise UsbIssError("Invalid clk_khz value")

    @staticmethod
    def _get_serial_divisor(baud_rate):
        divisor = (48000000 // (16 * baud_rate)) - 1
        divisor = max(divisor, 0)
        divisor = min(divisor, 0xFFFF)
        return [divisor >> 8, divisor & 0xFF]

    @staticmethod
    def _get_spi_divisor(clock_khz):
        divisor = (6000 // clock_khz) - 1
        divisor = max(divisor, 0)
        divisor = min(divisor, 0xFF)
        return divisor
