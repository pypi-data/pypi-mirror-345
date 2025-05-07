from jDWM import Ainslie
from jDWM import utilities
import numpy as np
from scipy.integrate import cumulative_trapezoid
import pytest

rng = np.random.default_rng(0)


def test_make_transition_matrix():
    N = 100
    r = np.linspace(0, 3, 100)
    U = rng.normal(size=N)
    V = rng.normal(size=N)
    visc = rng.normal(size=N)
    dx = 0.1

    ab1, B1 = Ainslie.make_transition_matrix(r, U, V, visc, dx)
    try:
        from jDWM import fAinslie
        ab2, B2 = fAinslie.make_transition_matrix(r, U, V, visc, dx)

        np.testing.assert_array_almost_equal(ab1, ab2)
        np.testing.assert_array_almost_equal(B1, B2)
    except ModuleNotFoundError:
        pytest.xfail('Fortran lid not found')


def test_evolve_explicit():
    N = 100
    r = np.linspace(0, 3, 100)
    U = rng.normal(size=N)
    V = rng.normal(size=N)
    visc = rng.normal(size=N)
    dx = 0.1
    dr = r[1] - r[0]
    Uout1, Vout1 = Ainslie.evolve_explicit(r, U, V, visc, dx, dr)

    try:
        from jDWM import fAinslie
        Uout2, Vout2 = fAinslie.evolve_explicit(r, U, V, visc, dx, dr)

        np.testing.assert_array_almost_equal(Uout1, Uout2)
        np.testing.assert_array_almost_equal(Vout1, Vout2)
    except ModuleNotFoundError:
        pytest.xfail('Fortran lid not found')


def test_calculate_radial_velocity():
    N = 100
    r = np.linspace(0, 3, 100)
    U_m = rng.normal(size=N)
    U_p = rng.normal(size=N)
    dx = 0.1
    dr = r[1] - r[0]
    V1 = Ainslie.calculate_radial_velocity(r, U_m, U_p, dr, dx)
    try:
        from jDWM import fAinslie
        V2 = fAinslie.calculate_radial_velocity(r, U_m, U_p, dr, dx)

        np.testing.assert_array_almost_equal(V1, V2)
    except ModuleNotFoundError:
        pytest.xfail('Fortran lid not found')


def test_wake_width():
    N = 100
    r = np.linspace(0, 3, N)
    U = np.ones_like(r)
    U[0:50] = 0

    width1 = utilities.wake_width(r, U)
    try:
        from jDWM.fortran import jdwm_fort
        width2 = jdwm_fort.wake_width(r, U, N)
        # np.testing.assert_array_almost_equal(width1, width2)
    except ModuleNotFoundError:
        pytest.xfail('Fortran lid not found')


def test_cumsum():
    x = np.arange(1, 11)
    n = len(x)
    ans1 = np.cumsum(x)
    try:
        from jDWM.fortran import jdwm_fort
        ans2 = jdwm_fort.cumsum(x, n)

        np.testing.assert_array_almost_equal(ans1, ans2)
    except ModuleNotFoundError:
        pytest.xfail('Fortran lid not found')


def test_cumtrapz():
    x = np.arange(1, 11)
    n = len(x)
    ans1 = cumulative_trapezoid(x, dx=0.1)
    try:
        from jDWM.fortran import jdwm_fort
        ans2 = jdwm_fort.cumtrapz(x, 0.1, n)

        np.testing.assert_array_almost_equal(ans1, ans2)
    except ModuleNotFoundError:
        pytest.xfail('Fortran lid not found')
