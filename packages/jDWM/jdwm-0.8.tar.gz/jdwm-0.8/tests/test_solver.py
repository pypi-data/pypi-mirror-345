import numpy as np
from jDWM.Wake import StaticWake
from jDWM import Ainslie
from pytest import fixture
from scipy import sparse
from jDWM.Ainslie import _make_transition_matrix


@fixture
def dwm():
    dwm = StaticWake(tsr=7, ct=0.5, TI=0.1)
    return dwm


def test_make_transition_matrix(dwm):
    r = np.arange(0, 1, 0.2)
    U = np.ones(5)
    V = np.zeros(5)
    visc = 0.5 * np.ones(5)
    dx = 0.1

    A_ref = np.array(
        [
            [35, -25, 0, 0, 0, ],
            [-6.25, 35, -18.75, 0, 0],
            [0, -9.375, 35, -15.625, 0],
            [0, 0, -10.41666667, 35, -14.58333333],
            [0, 0, 0, 0, 10],
        ]
    )

    ab, B = Ainslie.make_transition_matrix(r, U, V, visc, dx)
    A = sparse.diags([ab[2, :-1], ab[1, :], ab[0, 1:]], [-1, 0, 1], format="csc")
    np.testing.assert_allclose(A.todense(), A_ref)
    np.testing.assert_allclose(B, [10, 10, 10, 10, 10])
    ab_py, B_py = _make_transition_matrix(r, U, V, visc, dx)
    np.testing.assert_array_equal(ab, ab_py)
    np.testing.assert_array_equal(B, B_py)


def test_calculate_radial_velocity():
    r = np.arange(0, 1, 0.2)
    U_m = np.array([0.5, 0.5, 0.5, 1, 1])
    U_p = 1.1 * U_m
    dx = 0.1
    dr = r[1] - r[0]
    V = Ainslie.calculate_radial_velocity(r, U_m, U_p, dr, dx)
    V_py = Ainslie._calculate_radial_velocity(r, U_m, U_p, dr, dx)
    np.testing.assert_allclose(V, [0.0, -0.05, -0.1, -0.2, -0.325])
    np.testing.assert_array_equal(V, V_py)


def test_evolve(dwm):
    dr = 0.2
    r = np.arange(0, 1, dr)
    U = np.array([0.5, 0.5, 0.5, 1, 1])
    V = np.zeros(5)
    x = 0
    dx = 0.1

    visc = dwm.viscosity_model(x, r, U)
    U_out, V_out = Ainslie.evolve(r, U, V, visc, dx, dr)
    np.testing.assert_allclose(U_out, [0.5, 0.50000001, 0.5000781, 0.99997397, 1.0])
    np.testing.assert_allclose(
        V_out,
        [
            0.00000000e00,
            -1.46403542e-08,
            -7.81160485e-05,
            -7.81106265e-05,
            -3.90572114e-05,
        ],
    )
