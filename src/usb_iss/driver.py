import serial

from .exceptions import UsbIssError
from . import defs

# In Py2, bytes means str, and there's no immutable byte array defined.
# Use bytearray instead - this is mutable, but otherwise equivalent to
# Python3's bytes.
if isinstance(bytes(), str):
    bytes = bytearray

SERIAL_OPTS = {
    'baudrate': 9600,
    'parity': serial.PARITY_NONE,
    'bytesize': serial.EIGHTBITS,
    'stopbits': serial.STOPBITS_ONE,
    'xonxoff': False,
    'timeout': 0.5,
}


class Driver(object):
    """
    Internal serial port driver. Don't use this class directly.
    """
    def __init__(self):
        self._serial = None

    def open(self, port):
        self._serial = serial.Serial(port=port, **SERIAL_OPTS)
        return self

    def close(self):
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def write_cmd(self, command, data=None):
        if self._serial is None:
            raise UsbIssError("Serial port has not been opened")

        if data is None:
            data = []
        self._serial.write(bytes([command] + data))

    def read(self, byte_count):
        if self._serial is None:
            raise UsbIssError("Serial port has not been opened")

        data = list(self._serial.read(byte_count))
        if len(data) != byte_count:
            raise UsbIssError(
                "Expected %d bytes, but %d received" % (byte_count, len(data)))
        return data

    def check_i2c_ack(self):
        """For I2C, any non-zero code means ACK"""
        data = self.read(1)
        if data[0] == defs.ResponseCode.NACK.value:
            raise UsbIssError("Received NACK instead of ACK")

    def check_ack(self):
        data = self.read(1)
        if data[0] != defs.ResponseCode.ACK.value:
            raise UsbIssError("Received 0x%02X instead of ACK" % data[0])

    def check_ack_error_code(self, error_enum):
        data = self.read(2)
        if data[0] != defs.ResponseCode.ACK.value:
            raise UsbIssError(
                "Received %s [0x%02X, 0x%02X] instead of ACK"
                % (error_enum(data[1]), data[0], data[1]))
        return data[1]


class DummyDriver(object):
    """
    Dummy Driver object, used for testing.
    """
    def open(self, _):
        return self

    def close(self):
        pass

    def write_cmd(self, command, data=None):
        pass

    def read(self, byte_count):
        return list(range(byte_count))

    def check_i2c_ack(self):
        pass

    def check_ack(self):
        pass

    def check_ack_error_code(self, error_enum):
        return 0
