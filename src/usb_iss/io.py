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

        Params:
            io0: (integer) IO0 output level (0 to drive low, 1 to drive high).
            io1: (integer) IO1 output level (0 to drive low, 1 to drive high).
            io2: (integer) IO2 output level (0 to drive low, 1 to drive high).
            io3: (integer) IO3 output level (0 to drive low, 1 to drive high).
        """
        data = (((io0 & 0x01) << 0) +
                ((io1 & 0x01) << 1) +
                ((io2 & 0x01) << 2) +
                ((io3 & 0x01) << 3))
        self._drv.write_cmd(defs.IO_SET_PINS, [data])
        self._drv.check_ack()

    def get_pins(self):
        """
        Get the current state of all digital IO pins.

        Returns: (list(integer)):
            List containing the current state of the four digital IO pins.
        """
        self._drv.write_cmd(defs.IO_GET_PINS)
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

        If you try to convert a channel which is not set up an an analogue input,
        the result will be 0x0000.

        Params:
            pin: (integer) Input pin to sample.

        Returns: (integer)
            Sample value returned by the ADC (0-1023).
        """
        self._drv.write_cmd(defs.IO_GET_AD, [pin])
        data = self._drv.read(2)
        return (data[0] << 8) + data[1]
