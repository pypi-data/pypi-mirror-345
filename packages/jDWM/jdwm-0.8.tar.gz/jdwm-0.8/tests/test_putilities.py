import numpy as np
from jDWM.putilities import _wake_width, wake_width


def test_wake_width():
    r = np.arange(100)
    assert _wake_width(r, U=r) == wake_width(r, U=r) == 96.5
