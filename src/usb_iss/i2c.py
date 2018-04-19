from .exceptions import UsbIssError
from . import defs

I2C_RD = 0x01


class I2C(object):
    def __init__(self, drv):
        self._drv = drv

    def write_single(self, address, data_byte):
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2C_SGL, [address, data_byte])
        self._drv.check_i2c_ack()

    def read_single(self, address):
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2C_SGL, [address])
        return self._drv.read(1)[0]

    def write_ad0(self, address, data):
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2C_AD0, [address, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad0(self, address, byte_count):
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2C_AD0, [address, byte_count])
        return self._drv.read(byte_count)

    def write_ad1(self, address, register, data):
        if len(data) > defs.I2C_AD1_MAX_WRITE_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to write %d bytes, maximum is %d" %
                (len(data), defs.I2C_AD1_MAX_WRITE_BYTE_COUNT))
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2C_AD1,
                            [address, register, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad1(self, address, register, byte_count):
        if byte_count > defs.I2C_AD1_MAX_READ_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to read %d bytes, maximum is %d" %
                (byte_count, defs.I2C_AD1_MAX_READ_BYTE_COUNT))
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2C_AD1, [address, register, byte_count])
        return self._drv.read(byte_count)

    def write_ad2(self, address, register, data):
        if len(data) > defs.I2C_AD2_MAX_WRITE_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to write %d bytes, maximum is %d" %
                (len(data), defs.I2C_AD2_MAX_WRITE_BYTE_COUNT))
        address = address & ~I2C_RD
        reg_high = register >> 8
        reg_low = register & 0xFF
        self._drv.write_cmd(defs.I2C_AD2,
                            [address, reg_high, reg_low, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad2(self, address, register, byte_count):
        if byte_count > defs.I2C_AD2_MAX_READ_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to read %d bytes, maximum is %d" %
                (byte_count, defs.I2C_AD2_MAX_READ_BYTE_COUNT))
        address = address | I2C_RD
        reg_high = register >> 8
        reg_low = register & 0xFF
        self._drv.write_cmd(defs.I2C_AD2,
                            [address, reg_high, reg_low, byte_count])
        return self._drv.read(byte_count)

    def direct(self, data):
        self._drv.write_cmd(defs.I2C_DIRECT, data)
        bytes_to_read = self._drv.check_ack_error_code()
        if bytes_to_read == 0:
            return []
        return self._drv.read(bytes_to_read)

    def test(self, address):
        self._drv.write_cmd(defs.I2C_TEST, [address])
        return self._drv.read(1) != [defs.I2C_TEST_NO_DEVICE]
