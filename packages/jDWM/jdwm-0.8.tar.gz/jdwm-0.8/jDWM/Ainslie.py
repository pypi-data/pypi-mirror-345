import numpy as np
from scipy import integrate, linalg
from jDWM.utilities import jit


def evolve(r, U, V, visc, dx, dr):
    """
    Evolve the wake downstream by a single dx step.
    Args:
        r (1D array): radial positions along blade (nondimensional with radius).
        U (1D array): Axial wind speed over the blade (nondimensional).
        V (1D array): Radial wind speed over the blade (nondimensional).
        visc (1D array): Eddy viscosity over the blade (nondimensional).
        x (float): Current downstream distance, (nondimensional with radius).
        dx (float): downstream step size, (nondimensional with radius).
        dr (float): radial step size, (nondimensional with radius).
    Returns:
        U_out (1D array): Axial wind speed over the blade at a downstream
            distance x + dx (nondimensional).
        V_out (1D array): Radial wind speed over the blade at a downstream
            distance x + dx (nondimensional).
    """
    Nr = len(r)

    ab, B = make_transition_matrix(r, U, V, visc, dx)
    U_out = linalg.solve_banded((1, 1), ab, B)
    V_out = calculate_radial_velocity(r, U, U_out, dr, dx)

    return U_out, V_out


def evolve_explicit(r, U, V, visc, dx, dr):
    Nr = len(r)
    dr = r[1] - r[0]  # assume equidistant r
    assert Nr == len(U)
    assert Nr == len(V)

    U_out = np.zeros(Nr)
    a = np.zeros(Nr)
    d = np.zeros(Nr)

    a = visc / dr ** 2
    d[1:-1] = visc[1:-1] / (2 * r[1:-1] * dr) - V[1:-1] / (2 * dr)

    U_out[1:-1] = U[1:-1]
    U_out[1:-1] += dx * (-2 * a[1:-1])
    U_out[1:-1] += dx * (U[2:] / U[1:-1] * (a[1:-1] + d[1:-1]))
    U_out[1:-1] += dx * (U[:-2] / U[1:-1] * (a[1:-1] - d[1:-1]))

    U_out[0] = U[0] + 2 * dx * a[0] * (U[1] / U[0] - 1)
    U_out[-1] = U[-1]
    V_out = calculate_radial_velocity(r, U, U_out, dr, dx)

    return U_out, V_out


def _calculate_radial_velocity(r, U_m, U_p, dr, dx):
    """
    Calculates the radial velocity profile to satisfy the continuity equation.
    Args:
        r (1D array): radial positions along blade (nondimensional).
        U_m (1D array): Axial wind speed over the blade at previous time step (nondimensional).
        U_p (1D array):Axial wind speed over the blade at current time step (nondimensional).
        dr (float): radial discretisation (nondimensional).
        dx (float): axial discretisation (nondimensional).
    Returns:
        V_out (1D array): Radial wind speed over the blade at current time step (nondimensional).
    """
    dudx = (U_p - U_m) / dx
    V_out = np.zeros_like(r)
    # V_out[1:] = -integrate.cumtrapz(r * dudx, r) / r[1:]
    # jit-fiendly alternative
    rdudx = r * dudx
    V_out[1:] = -np.cumsum((rdudx[1:] + rdudx[:-1])) * dr / 2 / r[1:]
    return V_out


calculate_radial_velocity = jit(_calculate_radial_velocity)


def _make_transition_matrix(r, U, V, visc, dx):
    """
    Evolve the wake downstream by a single dx step.
    Args:
        r (1D array): radial positions along blade (nondimensional).
        U (1D array): Axial wind speed over the blade (nondimensional).
        V (1D array): Radial wind speed over the blade (nondimensional).
        visc (1D array): Eddy viscosity (nondimensional).
    Returns:
        ab ((3xNr) array): The A matrix in banded format in the system (Ax = B).
        B (1D array): The B matrix in the system to solve.
    """
    Nr = len(r)
    dr = r[1] - r[0]  # assume equidistant r
    assert Nr == len(U)
    assert Nr == len(V)

    V_ = np.zeros(Nr)
    V_m = np.zeros(Nr - 1)
    V_p = np.zeros(Nr - 1)

    V_m[:-1] += -V[1: Nr - 1] / (2 * dr)
    V_m[:-1] += visc[1: Nr - 1] / (2 * r[1: Nr - 1] * dr)
    V_m[:-1] += -visc[1: Nr - 1] / dr ** 2

    V_[1:-1] += U[1: Nr - 1] / dx
    V_[1:-1] += 2 * visc[1: Nr - 1] / dr ** 2

    V_p[1:] += V[1: Nr - 1] / (2 * dr)
    V_p[1:] += -visc[1: Nr - 1] / (2 * r[1: Nr - 1] * dr)
    V_p[1:] += -visc[1: Nr - 1] / dr ** 2

    # wake center boundary conditions
    V_[0] = U[0] / dx + 2 * visc[0] / dr ** 2
    V_p[0] = -2 * visc[0] / dr ** 2

    # wake edge boundary conditions
    V_m[-1] = 0
    V_[-1] = 1.0 / dx

    # Store the A matrix in banded structure compatible with LAPACK.
    ab = np.zeros((3, Nr))
    ab[0, 1:] = V_p
    ab[1, :] = V_
    ab[2, :-1] = V_m

    B = np.zeros(Nr)
    B[:-1] = U[:-1] ** 2 / dx
    B[-1] = U[Nr - 1] / dx

    return ab, B


make_transition_matrix = jit(_make_transition_matrix)
