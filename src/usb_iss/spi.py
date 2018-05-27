from .exceptions import UsbIssError
from . import defs


class SPI(object):
    """
    Use the USB_ISS device to perform SPI accesses.

    Example:
        ::

            from usb_iss import UsbIss

            # Configure SPI mode

            iss = UsbIss()
            iss.open("COM3")
            iss.setup_spi()

            # Write and read some data in a single transfer

            data = iss.spi.transfer([0, 1, 2]);

            print(data)
            # [4, 5, 6]
    """
    def __init__(self, drv):
        self._drv = drv

    def transfer(self, write_data):
        """
        Perform an SPI transfer.

        Args:
            write_data (list of int): List of bytes to write to the device
                during the transfer.
        Returns:
            list of int: List of bytes read from the device during the
            transfer.
        """
        if len(write_data) > defs.SPI_MAX_BYTE_COUNT:
            raise UsbIssError(
                "Attempted to write %d bytes, maximum is %d" %
                (len(write_data), defs.SPI_MAX_BYTE_COUNT))

        self._drv.write_cmd(defs.Command.SPI.value, write_data)
        self._drv.check_ack()
        return self._drv.read(len(write_data))
