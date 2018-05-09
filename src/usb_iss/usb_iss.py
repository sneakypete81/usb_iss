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
        Issue a ISS_MODE command to set the operating mode to I2C.

        Args:
            clock_khz (int): I2C clock rate in kHz.
                See https://www.robot-electronics.co.uk/htm/usb_iss_tech.htm
                for a list of valid values.
            use_i2c_hardware (bool): Use the USB_ISS module's hardware I2C
                controller.
            io1_type (defs.IOType): IO1 mode
                (default: DIGITAL_INPUT).
            io2_type (defs.IOType): IO2 mode
                (default: DIGITAL_INPUT).
        """
        if clock_khz == 20:
            assert not use_i2c_hardware
            i2c_mode = defs.Mode.I2C_S_20KHZ.value
        elif clock_khz == 50:
            assert not use_i2c_hardware
            i2c_mode = defs.Mode.I2C_S_50KHZ.value
        elif clock_khz == 100:
            i2c_mode = (defs.Mode.I2C_H_100KHZ.value if use_i2c_hardware else
                        defs.Mode.I2C_S_100KHZ.value)
        elif clock_khz == 400:
            i2c_mode = (defs.Mode.I2C_H_400KHZ.value if use_i2c_hardware else
                        defs.Mode.I2C_S_400KHZ.value)
        elif clock_khz == 1000:
            assert use_i2c_hardware
            i2c_mode = defs.Mode.I2C_H_1000KHZ.value
        else:
            raise UsbIssError("Invalid clk_khz value")

        io_type = io1_type.value | (io2_type.value << 2)
        data = [defs.SubCommand.ISS_MODE.value, i2c_mode, io_type]
        self._drv.write_cmd(defs.CMD_USB_ISS, data)
        self._drv.check_ack_error_code(defs.ModeError)

    def setup_i2c_serial(self):
        raise NotImplementedError

    def setup_spi(self):
        raise NotImplementedError

    def setup_io(self):
        raise NotImplementedError

    def change_io(self):
        raise NotImplementedError

    def setup_serial(self):
        raise NotImplementedError

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
