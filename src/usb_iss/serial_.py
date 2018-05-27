from .exceptions import UsbIssError
from . import defs


class Serial(object):
    """
    Use the USB_ISS device to perform Serial UART accesses.

    Example:
        ::

            from usb_iss import UsbIss

            # Configure Serial mode

            iss = UsbIss()
            iss.open("COM3")
            iss.setup_serial()

            # Write and read some data

            iss.serial.transmit([0x48, 0x65, 0x6c, 0x6c, 0x6f]);
            data = iss.serial.receive()

            print(data)
            # [72, 105]
    """
    def __init__(self, drv):
        self._drv = drv

    def transmit(self, data):
        """
        Transmit data over the Serial UART interface.

        Args:
            data (list of int): List of bytes to transmit.
        """
        self._drv.write_cmd(defs.Command.SERIAL.value, data)

    def receive(self):
        """
        Receive data over the Serial UART interface. Blocks until the receive
        buffer is non-empty.

        Returns:
            list of int: List of bytes received.
        """
        while True:
            rx_count = self.get_rx_count()
            if rx_count > 0:
                return self._drv.read(rx_count)

    def get_rx_count(self):
        """
        Check the status code and return the number of bytes in the receive
        buffer.

        Returns:
            int: Number of bytes in the receive buffer.
        """
        return self._get_status()[1]

    def get_tx_count(self):
        """
        Check the status code and return the number of bytes in the transmit
        buffer.

        Returns:
            int: Number of bytes in the transmit buffer.
        """
        return self._get_status()[0]

    def _get_status(self):
        [code, tx_count, rx_count] = self._drv.read(3)

        if code == defs.ResponseCode.NACK.value:
            raise UsbIssError("NACK received - transmit buffer overflow")

        return (tx_count, rx_count)
