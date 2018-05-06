from .exceptions import UsbIssError
from . import defs

I2C_RD = 0x01


class I2C(object):
    """
    USe the USB_ISS module to perform I2C accesses.

    Example::

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
    def __init__(self, drv):
        self._drv = drv

    def write(self, address, register, data):
        """
        Write multiple bytes to a device with a one-byte internal register
        address. The majority of devices will be written to using this method.
        This is an alias for the write_ad1 method.

        Params:
            address: (integer) I2C address of the device.
            register: (integer) Internal register address to write
                (0x00 - 0xFF).
            data: (list(integer)) List of bytes to write to the device.
        """
        self.write_ad1(address, register, data)

    def read(self, address, register, byte_count):
        """
        Read multiple bytes from a device with a one-byte internal register
        address. The majority of devices will be read from using this method.
        This is an alias for the read_ad1 method.

        Params:
            address: (integer) I2C address of the device.
            register: (integer) internal register address to read (0x00 - 0xFF).
            byte_count: (integer) Number of bytes to read.
        Returns: (list(integer))
            List of bytes read from the device.
        """
        return self.read_ad1(address, register, byte_count)

    def write_single(self, address, data_byte):
        """
        Write a single byte to an I2C device.

        Params:
            address: (integer) I2C address of the device.
            data_byte: (integer) Data byte to write to the device.
        """
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2C_SGL, [address, data_byte])
        self._drv.check_i2c_ack()

    def read_single(self, address):
        """
        Read a single byte from an I2C device.

        Params:
            address: (integer) I2C address of the device.
        Returns: (integer)
            data byte read from the device.
        """
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2C_SGL, [address])
        return self._drv.read(1)[0]

    def write_ad0(self, address, data):
        """
        Write multiple bytes to a device without internal register addressing,
        or where the internal register address does not require resetting.

        Params:
            address: (integer) I2C address of the device.
            data: (list(integer)) List of bytes to write to the device.
        """
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2C_AD0, [address, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad0(self, address, byte_count):
        """
        Read multiple bytes from a device without internal register addressing,
        or where the internal register address does not require resetting.

        Params:
            address: (integer) I2C address of the devie.
            byte_count: (integer) Number of bytes to read.
        Returns: (list(integer))
            List of bytes read from the device.
        """
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2C_AD0, [address, byte_count])
        return self._drv.read(byte_count)

    def write_ad1(self, address, register, data):
        """
        Write multiple bytes to a device with a one-byte internal register
        address. The majority of devices will be written to using this method.

        Params:
            address: (integer) I2C address of the device.
            register: (integer) Internal register address to write
                (0x00 - 0xFF).
            data: (list(integer)) List of bytes to write to the device.
        """
        if len(data) > defs.I2C_AD1_MAX_WRITE_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to write %d bytes, maximum is %d" %
                (len(data), defs.I2C_AD1_MAX_WRITE_BYTE_COUNT))
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2C_AD1,
                            [address, register, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad1(self, address, register, byte_count):
        """
        Read multiple bytes from a device with a one-byte internal register
        address. The majority of devices will be read from using this method.

        Params:
            address: (integer) I2C address of the device.
            register: (integer) internal register address to read (0x00 - 0xFF).
            byte_count: (integer) Number of bytes to read.
        Returns: (list(integer))
            List of bytes read from the device.
        """
        if byte_count > defs.I2C_AD1_MAX_READ_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to read %d bytes, maximum is %d" %
                (byte_count, defs.I2C_AD1_MAX_READ_BYTE_COUNT))
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2C_AD1, [address, register, byte_count])
        return self._drv.read(byte_count)

    def write_ad2(self, address, register, data):
        """
        Write multiple bytes to a device with a two-byte internal register
        address.

        Params:
            address: (integer) I2C address of the device.
            register: (integer) Internal register address to write
                (0x0000 - 0xFFFF).
            data: (list(integer)) List of bytes to write to the device.
        """
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
        """
        Read multiple bytes from a device with a two-byte internal register
        address.

        Params:
            address: (integer) I2C address of the device.
            register: (integer) internal register address to read
                (0x0000 - 0xFFFF).
            byte_count: (integer) Number of bytes to read.
        Returns: (list(integer))
            List of bytes read from the device.
        """
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
        """
        Send a custom I2C sequence to the device.
        See https://www.robot-electronics.co.uk/htm/usb_iss_i2c_tech.htm for a
        full set of examples.

        Params:
            data: (list(integer)) List of commands from defs.I2C_DIRECT_*.
        Returns: (list(integer))
            List of bytes read from the device.

        Example::

            # Equivalent to iss.i2c.write_single(0x40, 0x55)
            iss.i2c.direct([
                defs.I2C_DIRECT_START,
                defs.I2C_DIRECT_WRITE2,
                0x40,
                0x55,
                defs.I2C_DIRECT_STOP,
            ]);

        """
        self._drv.write_cmd(defs.I2C_DIRECT, data)
        bytes_to_read = self._drv.check_ack_error_code()
        if bytes_to_read == 0:
            return []
        return self._drv.read(bytes_to_read)

    def test(self, address):
        """
        Check whether a device responds to the specified I2C addresss.

        Params:
            address: (integer) I2C address of the device.

        Returns: (boolean)
            True if the device responds with an ACK.
        """
        self._drv.write_cmd(defs.I2C_TEST, [address])
        return self._drv.read(1) != [defs.I2C_TEST_NO_DEVICE]
