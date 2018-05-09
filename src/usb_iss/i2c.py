from .exceptions import UsbIssError
from . import defs

I2C_RD = 0x01


class I2C(object):
    """
    Use the USB_ISS module to perform I2C accesses.

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
    """
    def __init__(self, drv):
        self._drv = drv

    def write(self, address, register, data):
        """
        Write multiple bytes to a device with a one-byte internal register
        address. The majority of devices will be written to using this method.
        This is an alias for the write_ad1 method.

        Args:
            address (int): I2C address of the device.
            register (int): Internal register address to write
                (0x00 - 0xFF).
            data (list of int): List of bytes to write to the device.
        """
        self.write_ad1(address, register, data)

    def read(self, address, register, byte_count):
        """
        Read multiple bytes from a device with a one-byte internal register
        address. The majority of devices will be read from using this method.
        This is an alias for the read_ad1 method.

        Args:
            address (int): I2C address of the device.
            register (int): Internal register address to read (0x00 - 0xFF).
            byte_count (int): Number of bytes to read.
        Returns:
            list of int: List of bytes read from the device.
        """
        return self.read_ad1(address, register, byte_count)

    def write_single(self, address, data_byte):
        """
        Write a single byte to an I2C device.

        Args:
            address (int): I2C address of the device.
            data_byte (int): Data byte to write to the device.
        """
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2CCommand.I2C_SGL.value,
                            [address, data_byte])
        self._drv.check_i2c_ack()

    def read_single(self, address):
        """
        Read a single byte from an I2C device.

        Args:
            address (int): I2C address of the device.
        Returns:
            int: Data byte read from the device.
        """
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2CCommand.I2C_SGL.value, [address])
        return self._drv.read(1)[0]

    def write_ad0(self, address, data):
        """
        Write multiple bytes to a device without internal register addressing,
        or where the internal register address does not require resetting.

        Args:
            address (int): I2C address of the device.
            data (list of int): List of bytes to write to the device.
        """
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2CCommand.I2C_AD0.value,
                            [address, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad0(self, address, byte_count):
        """
        Read multiple bytes from a device without internal register addressing,
        or where the internal register address does not require resetting.

        Args:
            address (int): I2C address of the devie.
            byte_count (int): Number of bytes to read.
        Returns:
            list of int: List of bytes read from the device.
        """
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2CCommand.I2C_AD0.value,
                            [address, byte_count])
        return self._drv.read(byte_count)

    def write_ad1(self, address, register, data):
        """
        Write multiple bytes to a device with a one-byte internal register
        address.

        Args:
            address (int): I2C address of the device.
            register (int): Internal register address to write (0x00 - 0xFF).
            data (list of int): List of bytes to write to the device.
        """
        if len(data) > defs.I2C_AD1_MAX_WRITE_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to write %d bytes, maximum is %d" %
                (len(data), defs.I2C_AD1_MAX_WRITE_BYTE_COUNT))
        address = address & ~I2C_RD
        self._drv.write_cmd(defs.I2CCommand.I2C_AD1.value,
                            [address, register, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad1(self, address, register, byte_count):
        """
        Read multiple bytes from a device with a one-byte internal register
        address.

        Args:
            address (int): I2C address of the device.
            register (int): Internal register address to read (0x00 - 0xFF).
            byte_count (int): Number of bytes to read.
        Returns:
            list of int: List of bytes read from the device.
        """
        if byte_count > defs.I2C_AD1_MAX_READ_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to read %d bytes, maximum is %d" %
                (byte_count, defs.I2C_AD1_MAX_READ_BYTE_COUNT))
        address = address | I2C_RD
        self._drv.write_cmd(defs.I2CCommand.I2C_AD1.value,
                            [address, register, byte_count])
        return self._drv.read(byte_count)

    def write_ad2(self, address, register, data):
        """
        Write multiple bytes to a device with a two-byte internal register
        address.

        Args:
            address (int): I2C address of the device.
            register (int): Internal register address to write
                (0x0000 - 0xFFFF).
            data (list of int): List of bytes to write to the device.
        """
        if len(data) > defs.I2C_AD2_MAX_WRITE_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to write %d bytes, maximum is %d" %
                (len(data), defs.I2C_AD2_MAX_WRITE_BYTE_COUNT))
        address = address & ~I2C_RD
        reg_high = register >> 8
        reg_low = register & 0xFF
        self._drv.write_cmd(defs.I2CCommand.I2C_AD2.value,
                            [address, reg_high, reg_low, len(data)] + data)
        self._drv.check_i2c_ack()

    def read_ad2(self, address, register, byte_count):
        """
        Read multiple bytes from a device with a two-byte internal register
        address.

        Args:
            address (int): I2C address of the device.
            register (int): Internal register address to read
                (0x0000 - 0xFFFF).
            byte_count (int): Number of bytes to read.
        Returns:
            list of int: List of bytes read from the device.
        """
        if byte_count > defs.I2C_AD2_MAX_READ_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to read %d bytes, maximum is %d" %
                (byte_count, defs.I2C_AD2_MAX_READ_BYTE_COUNT))
        address = address | I2C_RD
        reg_high = register >> 8
        reg_low = register & 0xFF
        self._drv.write_cmd(defs.I2CCommand.I2C_AD2.value,
                            [address, reg_high, reg_low, byte_count])
        return self._drv.read(byte_count)

    def direct(self, data):
        """
        Send a custom I2C sequence to the device.
        See https://www.robot-electronics.co.uk/htm/usb_iss_i2c_tech.htm for a
        full set of examples.

        Args:
            data (list of defs.I2CDirect): List of
                :class:`~usb_iss.defs.I2CDirect` commands and data.

        Returns:
            list of int: List of bytes read from the device.

        Example:
            ::

                # Equivalent to iss.i2c.write_single(0x40, 0x55)
                iss.i2c.direct([
                    defs.I2CDirect.START,
                    defs.I2CDirect.WRITE2,
                    0x40,
                    0x55,
                    defs.I2CDirect.STOP,
                ]);

        """
        # Convert any I2CDirect items to the corresponding value
        def convert_to_value(byte):
            if isinstance(byte, defs.I2CDirect):
                return byte.value
            else:
                return byte
        bytes = [convert_to_value(byte) for byte in data]

        self._drv.write_cmd(defs.I2CCommand.I2C_DIRECT.value, bytes)
        bytes_to_read = self._drv.check_ack_error_code(defs.I2CDirectError)
        if bytes_to_read == 0:
            return []
        return self._drv.read(bytes_to_read)

    def test(self, address):
        """
        Check whether a device responds at the specified I2C addresss.

        Args:
            address (int): I2C address of the device.

        Returns:
            bool: True if the device responds with an ACK.
        """
        self._drv.write_cmd(defs.I2CCommand.I2C_TEST.value, [address])
        return self._drv.read(1) != [defs.I2CTestResponse.NO_DEVICE.value]
