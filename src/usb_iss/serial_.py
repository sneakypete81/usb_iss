from datetime import datetime, timedelta

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
            iss.serial.transmit_string("Hello!")
            data = iss.serial.receive()

            print(data)
            # [72, 105]
    """
    def __init__(self, drv):
        self._drv = drv
        self._rx_buffer = []

    def transmit(self, data):
        """
        Transmit data over the Serial UART interface.

        Args:
            data (list of int): List of bytes to transmit.
        """
        self._transaction(data)

    def transmit_string(self, string, encoding="utf-8"):
        """
        Transmit a string over the Serial UART interface.

        Args:
            string (str): String to transmit.
            encoding (str): Encoding of the string.
        """
        data = list(bytearray(string.encode(encoding)))
        self.transmit(data)

    def receive(self, timeout_ms=100):
        """
        Receive data over the Serial UART interface. Returns once no data is
        received for timeout_ms.

        Args:
            timeout_ms (int): Returns once no data is received for this period.
        Returns:
            list of int: List of bytes received.
        """
        data = []
        last_rx_time = datetime.now()

        while True:
            rx_count = self.get_rx_count()
            if rx_count > 0:
                data += self._rx_buffer
                self._rx_buffer = []
                last_rx_time = datetime.now()

            deadline = last_rx_time + timedelta(milliseconds=timeout_ms)
            if datetime.now() > deadline:
                return data

    def receive_string(self, timeout_ms=100, encoding="utf-8"):
        """
        Receive a string over the Serial UART interface. Returns once no data
        is received for timeout_ms.

        Args:
            timeout_ms (int): Returns once no data is received for this period.
            encoding (str): Encoding of the string.
        Returns:
            string: String received.
        """
        return bytearray(self.receive(timeout_ms)).decode(encoding)

    def get_rx_count(self):
        """
        Return the number of bytes in the receive buffer.

        Returns:
            int: Number of bytes in the receive buffer.
        """
        self._transaction()
        return len(self._rx_buffer)

    def get_tx_count(self):
        """
        Return the number of bytes in the transmit buffer.

        Returns:
            int: Number of bytes in the transmit buffer.
        """
        return self._transaction()

    def _transaction(self, data=None):
        if data is None:
            data = []
        self._drv.write_cmd(defs.Command.SERIAL.value, data)

        [code, tx_count, rx_count] = self._drv.read(3)

        if code == defs.ResponseCode.NACK.value:
            raise UsbIssError("NACK received - transmit buffer overflow")

        if rx_count > 0:
            self._rx_buffer += self._drv.read(rx_count)

        return tx_count
