from . import defs
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
    Example usage::

        from usb_iss import UsbIss, defs

        # Configure I2C mode

        iss = UsbIss()
        iss.open("COM3")
        iss.setup_i2c(defs.ISS_MODE_I2C_H_100KHZ)

        # Write and read back some data

        iss.i2c.write(0xC4, 0, [0, 1, 2]);
        data = iss.i2c.read(0xC4, 0, 3)

        print(data)
        # [0, 1, 2]
    """
    def __init__(self, dummy=False):
        self._drv = DummyDriver() if dummy else Driver()
        self.i2c = I2C(self._drv)
        self.io = IO(self._drv)

    def open(self, port):
        """
        Open the specified serial port for communication with the USB_ISS module.

        Param:
            port (string) - Serial port to use for usb_iss communication.
        """
        self._drv.open(port)
        return self

    def close(self):
        """
        Close the serial port.
        """
        self._drv.close()

    def setup_io(self):
        raise NotImplementedError

    def change_io(self):
        raise NotImplementedError

    def setup_i2c(self, i2c_mode,
                  io1_type=defs.IO_TYPE_IO1_DIGITAL_INPUT,
                  io2_type=defs.IO_TYPE_IO2_DIGITAL_INPUT):
        """
        Issue a ISS_MODE command to set the operating mode to I2C.

        Params:
            i2c_mode (integer) - I2C option from defs.ISS_MODE_I2C_*.
            io1_type (integer) - IO option from defs.IO_TYPE_IO1_*
                (default: IO_TYPE_IO1_DIGITAL_INPUT).
            io2_type (integer) - IO option from defs.IO_TYPE_IO2_*
                (default: IO_TYPE_IO2_DIGITAL_INPUT).
        """
        assert io1_type in defs.IO1_TYPES
        assert io2_type in defs.IO2_TYPES

        io_type = io1_type | io2_type
        data = [defs.USB_ISS_ISS_MODE, i2c_mode, io_type]
        self._drv.write_cmd(defs.CMD_USB_ISS, data)
        self._drv.check_ack_error_code()

    def setup_i2c_serial(self):
        raise NotImplementedError

    def setup_spi(self):
        raise NotImplementedError

    def setup_serial(self):
        raise NotImplementedError

    def read_module_id(self):
        """
        Returns: (integer)
            The USB_ISS module ID (always 7).
        """
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_ISS_VERSION])
        return self._drv.read(3)[0]

    def read_fw_version(self):
        """
        Returns: (integer)
            The USB_ISS firmware version.
        """
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_ISS_VERSION])
        return self._drv.read(3)[1]

    def read_iss_mode(self):
        """
        Returns: (integer)
            The current ISS_MODE operating mode. See defs.ISS_MODE_*.
        """
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_ISS_VERSION])
        return self._drv.read(3)[2]

    def read_serial_number(self):
        """
        Returns: (string)
            The serial number of the attached USB_ISS module.
        """
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_GET_SER_NUM])
        return bytes(self._drv.read(8)).decode('ascii')
