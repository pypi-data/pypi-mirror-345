import sys
import os
import pytest

try:
    from simulcrypt.CWG import ControlWordGenerator as CWG
except ImportError:
    sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), ".."), "src"))
    from simulcrypt.CWG import ControlWordGenerator as CWG


def test_64bit_key():
    """Make 8 bytes long CW by default."""
    cwg = CWG()
    assert len(cwg.cw(1)) == CWG.DEFAULT_CW_LEN

def test_128bit_key():
    """Make 16 bytes long CW per request."""
    cwg = CWG(16)
    assert len(cwg.cw(1)) == 16

def test_store_future_cw():
    """Store some more CW for (re)use in future."""
    cwg = CWG()
    _ = cwg.cw(0)
    # pylint: disable=W0212
    assert len(cwg._store) == CWG.DEFAULT_KEEP
    cwg = CWG(keep=8)
    _ = cwg.cw(0)
    assert len(cwg._store) == 8

def test_cw_store_size():
    """Store only relevant CW, delete any previous CW."""
    cwg = CWG()
    _ = cwg.cw(0)
    # pylint: disable=W0212
    assert len(cwg._store) == CWG.DEFAULT_KEEP
    assert list(cwg._store.keys()) == [0, 1, 2]
    _ = cwg.cw(2)
    assert len(cwg._store) == CWG.DEFAULT_KEEP
    assert list(cwg._store.keys()) == [2, 3, 4]
    _ = cwg.cw(65535)
    assert len(cwg._store) == CWG.DEFAULT_KEEP
    assert list(cwg._store.keys()) == [65535, 0, 1]

def test_future_cw_usage():
    """Reuse future CW from CW store."""
    cwg = CWG()
    cw1 = cwg.cw(0)
    # pylint: disable=W0212
    future_cw2 = cwg._store[1]
    future_cw3 = cwg._store[2]
    cw2 = cwg.cw(1)
    cw3 = cwg.cw(2)
    cw4 = cwg.cw(3)
    assert cw2 == future_cw2
    assert cw3 == future_cw3
    assert cw4 != cw1

def test_crypto_period_number_is_int():
    cwg = CWG()
    with pytest.raises(TypeError):
        _ = cwg.cw('0')

def test_crypto_period_number_16bit_range():
    cwg = CWG()
    with pytest.raises(ValueError):
        _ = cwg.cw(-1)
    with pytest.raises(ValueError):
        _ = cwg.cw(65536)
