from . import defs


class IO(object):
    def __init__(self, drv):
        self._drv = drv

    def set_pins(self, io0, io1, io2, io3):
        data = (((io0 & 0x01) << 0) +
                ((io1 & 0x01) << 1) +
                ((io2 & 0x01) << 2) +
                ((io3 & 0x01) << 3))
        self._drv.write_cmd(defs.IO_SET_PINS, [data])
        self._drv.check_ack()

    def get_pins(self):
        self._drv.write_cmd(defs.IO_GET_PINS)
        data = self._drv.read(1)[0]
        return [(data >> 0) & 0x01,
                (data >> 1) & 0x01,
                (data >> 2) & 0x01,
                (data >> 3) & 0x01]

    def get_ad(self, pin):
        self._drv.write_cmd(defs.IO_GET_AD, [pin])
        data = self._drv.read(2)
        return (data[0] << 8) + data[1]
