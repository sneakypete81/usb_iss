"""
Definitions defined at http://www.robot-electronics.co.uk/htm/usb_iss_tech.htm
"""
from enum import Enum

# USB-ISS command
CMD_USB_ISS = 0x5A


class ResponseCode(Enum):
    """
    Note: For I2C, NACK = 0x00, ACK = Non-zero.
    """
    NACK = 0x00
    ACK = 0xFF


class SubCommand(Enum):
    ISS_VERSION = 0x01
    ISS_MODE = 0x02
    GET_SER_NUM = 0x03


class Mode(Enum):
    IO_MODE = 0x00
    IO_CHANGE = 0x10
    I2C_S_20KHZ = 0x20
    I2C_S_50KHZ = 0x30
    I2C_S_100KHZ = 0x40
    I2C_S_400KHZ = 0x50
    I2C_H_100KHZ = 0x60
    I2C_H_400KHZ = 0x70
    I2C_H_1000KHZ = 0x80
    SPI_MODE = 0x90
    SERIAL = 0x01


class ModeError(Enum):
    UNKNOWN_COMMAND = 0x05
    INTERNAL_ERROR_1 = 0x06
    INTERNAL_ERROR_2 = 0x07


class IOType(Enum):
    NULL = 0x00
    OUTPUT_LOW = 0x00
    OUTPUT_HIGH = 0x01
    DIGITAL_INPUT = 0x02
    ANALOGUE_INPUT = 0x03


class SPIMode(Enum):
    TX_ACTIVE_TO_IDLE_IDLE_LOW = 0x90
    TX_ACTIVE_TO_IDLE_IDLE_HIGH = 0x91
    TX_IDLE_TO_ACTIVE_IDLE_LOW = 0x92
    TX_IDLE_TO_ACTIVE_IDLE_HIGH = 0x93


class I2CCommand(Enum):
    I2C_SGL = 0x53
    I2C_AD0 = 0x54
    I2C_AD1 = 0x55
    I2C_AD2 = 0x56
    I2C_DIRECT = 0x57
    I2C_TEST = 0x58


# Maximum number of bytes that can be read/written in a single command
I2C_AD1_MAX_WRITE_BYTE_COUNT = 60
I2C_AD1_MAX_READ_BYTE_COUNT = 60
I2C_AD2_MAX_WRITE_BYTE_COUNT = 59
I2C_AD2_MAX_READ_BYTE_COUNT = 64


class I2CDirect(Enum):
    START = 0x01
    RESTART = 0x02
    STOP = 0x03
    NACK = 0x04
    READ1 = 0x20
    READ2 = 0x21
    READ3 = 0x22
    READ4 = 0x23
    READ5 = 0x24
    READ6 = 0x25
    READ7 = 0x26
    READ8 = 0x27
    READ9 = 0x28
    READ10 = 0x29
    READ11 = 0x2A
    READ12 = 0x2B
    READ13 = 0x2C
    READ14 = 0x2D
    READ15 = 0x2E
    READ16 = 0x2F
    WRITE1 = 0x30
    WRITE2 = 0x31
    WRITE3 = 0x32
    WRITE4 = 0x33
    WRITE5 = 0x34
    WRITE6 = 0x35
    WRITE7 = 0x36
    WRITE8 = 0x37
    WRITE9 = 0x38
    WRITE10 = 0x39
    WRITE11 = 0x3A
    WRITE12 = 0x3B
    WRITE13 = 0x3C
    WRITE14 = 0x3D
    WRITE15 = 0x3E
    WRITE16 = 0x3F


class I2CDirectError(Enum):
    DEVICE_ERROR = 0x01
    BUFFER_OVERFLOW = 0x02
    BUFFER_UNDERFLOW = 0x03
    UNKNOWN_COMMAND = 0x04


class I2CTestResponse(Enum):
    """ Nonzero means device was found """
    NO_DEVICE = 0x00


class IOCommand(Enum):
    SET_PINS = 0x63
    GET_PINS = 0x64
    GET_AD = 0x65
