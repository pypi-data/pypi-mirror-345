# pylint: disable=C0103
from random import randint


class ControlWordGenerator:
    """Basic Control Word (aka Service Key) Generator implementation
    including CW values store for three future crypto-periods.
    """

    DEFAULT_CW_LEN = 8    # normally 8 or 16 bytes (64 or 128 bits)
    DEFAULT_KEEP = 3      # number of CW to keep in memory

    def __init__(self, size: int = DEFAULT_CW_LEN, keep: int = DEFAULT_KEEP):
        self._store = {}
        self._size = size
        self._keep = keep

    def __repr__(self):
        return f'{self.__class__.__name__}(size={self._size}, keep={self._keep})'

    def _cp_num_reset(self, n: int) -> int:
        """Adjust crypto-period number to 16-bit value range."""
        if n <= 65535:
            return n
        return n - 65536

    def _rand_cw(self, size: int = DEFAULT_CW_LEN) -> bytes:
        """Return (size) random bytes as a new Control Word (aka Service Key)."""
        return b''.join([int.to_bytes(randint(0, 255), length=1) for _ in range(size)])

    def cw(self, cp_num: int) -> bytes:
        """Return CW for crypto-period number, make and store two more
        for next ones and remove any previous CW from store.
        """
        if not isinstance(cp_num, int):
            raise TypeError('cp_num(ber) should be int')
        if not 0 <= cp_num <= 65535:
            raise ValueError('cp_num(ber) should be in range 0-65535')
        cp_numbers = list(map(self._cp_num_reset, range(cp_num, cp_num+self._keep)))
        for cp in cp_numbers:
            if cp not in self._store:
                self._store[cp] = self._rand_cw(self._size)
        # remove previous crypto-period CW
        if cp_num == 0 and 65535 in self._store:
            del self._store[65535]
        elif cp_num-1 in self._store:
            del self._store[cp_num-1]
        # remove unused CWs if any (just in case)
        if len(self._store) > self._keep:
            for key in list(self._store.keys()):
                if key not in cp_numbers:
                    del self._store[key]
        return self._store[cp_num]
