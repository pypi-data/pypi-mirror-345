from .fortran import jdwm_fort
from scipy import linalg


def evolve(r, U, V, visc, dx, dr):  # pragma: no cover

    Nr = len(r)
    ab, B = make_transition_matrix(r, U, V, visc, dx)
    U_out = linalg.solve_banded((1, 1), ab, B)
    V_out = calculate_radial_velocity(r, U, U_out, dr, dx)

    return U_out, V_out


def evolve_explicit(r, U, V, visc, dx, dr):  # pragma: no cover

    Nr = len(r)
    U_out, V_out = jdwm_fort.evolve_explicit(r, U, V, visc, dx, Nr)

    return U_out, V_out


def calculate_radial_velocity(r, U_m, U_p, dr, dx):  # pragma: no cover

    Nr = len(r)
    V_out = jdwm_fort.calculate_radial_velocity(r, U_m, U_p, dr, dx, Nr)
    return V_out


def make_transition_matrix(r, U, V, visc, dx):  # pragma: no cover

    Nx = len(r)
    ab, B = jdwm_fort.make_transition_matrix(r, U, V, visc, dx, Nx)
    return ab, B
