import numpy as np
from jDWM import utilities


def test_wake_width():
    r = np.linspace(0, 3, 100)
    U = np.ones_like(r)
    U[0:50] = 0

    width = utilities.wake_width(r, U)
    np.testing.assert_almost_equal(width, 1.409090909090909)


def test_wake_width_zero_total_def():
    r = np.linspace(0, 3, 100)
    U = np.ones_like(r)

    width = utilities.wake_width(r, U)
    assert width == 0


def test_rotor_area_mean():

    r = np.linspace(0, 3, 1000)
    U = r

    rotor_area_mean = utilities.rotor_area_mean(r, U)
    np.testing.assert_almost_equal(rotor_area_mean, 2 / 3, decimal=4)
