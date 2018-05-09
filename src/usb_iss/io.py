from . import defs


class IO(object):
    """
    Use the USB_ISS module to perform IO accesses.
    """
    def __init__(self, drv):
        self._drv = drv

    def set_pins(self, io0, io1, io2, io3):
        """
        Set the digital output pins high or low. This command only operates on
        pins that have been configured as digital outputs. Digital or analogue
        inputs or pins that are used for I2C or serial are not affected.

        For each argument, set to 0 to drive low and 1 to drive high.

        Args:
            io0 (int): IO0 output value.
            io1 (int): IO1 output value.
            io2 (int): IO2 output value.
            io3 (int): IO3 output value.
        """
        data = (((io0 & 0x01) << 0) +
                ((io1 & 0x01) << 1) +
                ((io2 & 0x01) << 2) +
                ((io3 & 0x01) << 3))
        self._drv.write_cmd(defs.IOCommand.SET_PINS.value, [data])
        self._drv.check_ack()

    def get_pins(self):
        """
        Get the current state of all digital IO pins.

        Returns:
            list of int: List containing the current state of the four digital
            IO pins (0 = low, 1 = high).
        """
        self._drv.write_cmd(defs.IOCommand.GET_PINS.value)
        data = self._drv.read(1)[0]
        return [(data >> 0) & 0x01,
                (data >> 1) & 0x01,
                (data >> 2) & 0x01,
                (data >> 3) & 0x01]

    def get_ad(self, pin):
        """
        Get a ADC sample from the specified analogue input pin.

        This uses a 10-bit ADC, so the result is between 0-1023 for the voltage
        swing between VSS and VCC.

        Args:
            pin (int): Input pin to sample.

        Returns:
            int: Sample value returned by the ADC (0-1023).
        """
        self._drv.write_cmd(defs.IOCommand.GET_AD.value, [pin])
        data = self._drv.read(2)
        return (data[0] << 8) + data[1]
