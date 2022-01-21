"""
Definitions from http://www.robot-electronics.co.uk/htm/usb_iss_tech.htm.
"""
from enum import Enum


class Command(Enum):
    """
    Command code sent as the first byte.
    """
    I2C_SGL = 0x53
    I2C_AD0 = 0x54
    I2C_AD1 = 0x55
    I2C_AD2 = 0x56
    I2C_DIRECT = 0x57
    I2C_TEST = 0x58
    USB_ISS = 0x5A
    SPI = 0x61
    SERIAL = 0x62
    SET_PINS = 0x63
    GET_PINS = 0x64
    GET_AD = 0x65


class SubCommand(Enum):
    """
    Internal subcommand used with Command.USB_ISS.
    """
    ISS_VERSION = 0x01
    ISS_MODE = 0x02
    GET_SER_NUM = 0x03


class Mode(Enum):
    """
    USB-ISS module operating modes.
    """
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
    SERIAL_I2C_S_20KHZ = 0x21
    SERIAL_I2C_S_50KHZ = 0x31
    SERIAL_I2C_S_100KHZ = 0x41
    SERIAL_I2C_S_400KHZ = 0x51
    SERIAL_I2C_H_100KHZ = 0x61
    SERIAL_I2C_H_400KHZ = 0x71
    SERIAL_I2C_H_1000KHZ = 0x81


class IOType(Enum):
    """
    IO configuration for a single pin.
    """
    OUTPUT_LOW = 0x00
    OUTPUT_HIGH = 0x01
    DIGITAL_INPUT = 0x02
    ANALOGUE_INPUT = 0x03


class SPIMode(Enum):
    """
    SPI clock phase setting.
    """
    TX_ACTIVE_TO_IDLE_IDLE_LOW = 0x90
    TX_ACTIVE_TO_IDLE_IDLE_HIGH = 0x91
    TX_IDLE_TO_ACTIVE_IDLE_LOW = 0x92
    TX_IDLE_TO_ACTIVE_IDLE_HIGH = 0x93


class I2CDirect(Enum):
    """
    I2C_DIRECT commands.
    """
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


class ResponseCode(Enum):
    """
    First byte of a response.
    Note: For I2C: NACK = 0x00, ACK = Non-zero.
    """
    NACK = 0x00
    ACK = 0xFF


class ModeError(Enum):
    """
    Error codes for the mode setting commands (second byte of the response).
    """
    UNKNOWN_COMMAND = 0x05
    INTERNAL_ERROR_1 = 0x06
    INTERNAL_ERROR_2 = 0x07


class I2CDirectError(Enum):
    """
    Error codes for the I2C_DIRECT command (second byte of the response).
    """
    DEVICE_ERROR = 0x01
    BUFFER_OVERFLOW = 0x02
    BUFFER_UNDERFLOW = 0x03
    UNKNOWN_COMMAND = 0x04


# Maximum number of bytes that can be read/written in a single command
I2C_AD1_MAX_WRITE_BYTE_COUNT = 60
I2C_AD1_MAX_READ_BYTE_COUNT = 60
I2C_AD2_MAX_WRITE_BYTE_COUNT = 59
I2C_AD2_MAX_READ_BYTE_COUNT = 64
SPI_MAX_BYTE_COUNT = 62
