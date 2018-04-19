from . import defs
from .driver import Driver
from .i2c import I2C
from .io import IO

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray


class UsbIss(object):
    def __init__(self):
        self._drv = Driver()
        self.i2c = I2C(self._drv)
        self.io = IO(self._drv)

    def open(self, port):
        self._drv.open(port)
        return self

    def close(self):
        self._drv.close()

    def setup_io(self):
        raise NotImplementedError

    def change_io(self):
        raise NotImplementedError

    def setup_i2c(self, i2c_mode, io1_type, io2_type):
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
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_ISS_VERSION])
        return self._drv.read(3)[0]

    def read_fw_version(self):
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_ISS_VERSION])
        return self._drv.read(3)[1]

    def read_iss_mode(self):
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_ISS_VERSION])
        return self._drv.read(3)[2]

    def read_serial_number(self):
        self._drv.write_cmd(defs.CMD_USB_ISS, [defs.USB_ISS_GET_SER_NUM])
        return bytes(self._drv.read(8)).decode('ascii')
