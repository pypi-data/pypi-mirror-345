import numpy as np
from scipy import sparse
# from pydantic import BaseModel
from . import Ainslie
from jDWM.utilities import jit
# from pydantic.config import ConfigDict

try:
    trapz_fun = np.trapezoid  # Numpy 2
except AttributeError:
    trapz_fun = np.trapz  # Numpy 1


class CustomBaseModel():
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():

            if hasattr(self, k) or k in self.__class__.__annotations__:
                setattr(self, k, v)
        for k, v in self.__dict__.items():
            if isinstance(v, CustomBaseModel):
                v.update(**kwargs)

    @classmethod
    def get_subclass(cls, name):
        for _cls in cls.__subclasses__():
            if _cls.__name__.lower() == name.lower():
                return _cls

        else:
            raise AttributeError(f"{name} not found among {cls.__name__} models.")


def cart2offcentrecylindrical(X, Y, Z, center_x, center_y, center_z):
    """
    Transforms points in cartesian space into off-center cylindrical
    coordinates. The cylinder center varies in the y and z plane with
    respect to the longitudinal axis, x.
    """
    i_upper = np.searchsorted(center_x, X)
    i_upper[i_upper == len(center_x)] = 0
    i_lower = i_upper - 1

    diff = (center_x[i_upper] - center_x[i_lower])
    w = (X - center_x[i_lower]) / diff

    C = abs(
        (1 - w) * np.sqrt((Y - center_y[i_lower]) ** 2 + (Z - center_z[i_lower]) ** 2)
        + w * np.sqrt((Y - center_y[i_upper]) ** 2 + (Z - center_z[i_upper]) ** 2)
    )

    return X, C


def masked_interpolation(interpolator, mask, points, fill_value=0):
    """
    Executes scipy interpolation only on masked points. Unmasked points receive
    the fill value.
    """
    if mask.sum() == 0:
        return fill_value * np.ones_like(mask, dtype=float)

    # Calculate sparse matrix layout from mask.
    mask_sp = sparse.csr_matrix(mask)
    masked_points = tuple(x[mask] for x in points)

    # Run interpolation on masked points and store in sparse layout.
    out_sparse = sparse.csr_matrix(
        (interpolator(masked_points), mask_sp.indices, mask_sp.indptr)
    )
    # Convert output to dense form with fill values in unmasked points
    out_sparse.resize((1, len(mask)))
    out = fill_value * np.ones_like(mask, dtype=float)
    out[mask] = out_sparse.data
    return out


def _wake_width(r, U):
    """
    Returns the width (radius) of the wake. Finds the radius which encapsulates 95%
    of the deficit.

    Args:
        r (1D array): radial positions (nondimensional)
        U (1D array): Axial wind speed over the blade (nondimensional).

    Returns:
        width (float): Wake radius, (nondimensional with radius).
    """
    #dr = np.diff(r)
    dr = r[1:] - r[:-1]
    r_mid = r[:-1] + dr / 2
    dA = np.pi * (r[1:] ** 2 - r[:-1] ** 2)

    total_def = np.sum((1 - U[1:]) * dA)
    cumulative_def = np.cumsum((1 - U[1:]) * dA)

    if total_def == 0:
        return 0

    in_deficit = (cumulative_def / total_def) < 0.95
    if in_deficit.sum() == 0:
        width = 0
    else:
        width = r_mid[in_deficit].max()

    return width


wake_width = jit(_wake_width)


def rotor_area_mean(r, x, rmax=1):
    """
    Returns the rotor area mean of the quantity, x(r). The rotor mean is defined as
    the area-weighted average of a quantity x(r), which is a function of radial position.
    For example, rotor mean wind speed, or rotor mean induction.

    The rotor_area_mean ignores x(r) such that r > rmax (usually 1)

    Args:
        r (1D array): radial positions (nondimensional)
        x (1D array): Quantity to be averaged.

    Returns:
        rotor_area_mean (float): Rotor area mean of x(r).
    """

    assert len(r) == len(x)
    r1 = np.linspace(0, 1, 100)
    x1 = np.interp(r1, r, x)

    r, x = r[r <= rmax], x[r <= rmax]
    rotor_area_mean = 2 * trapz_fun(r * x, r)
    return 2 * trapz_fun(r1 * x1, r1)
    return rotor_area_mean


def load_mann(filename, N=(32, 32)):
    """
    Loads a mann turbulence box.

    Args:
        filename (str): Filename of turbulence box
        N (tuple): Number of grid points (ny, nz) or (nx, ny, nz)

    Returns:
        turbulence_box (nd_array): turbulent box data as 3D array,
    """
    data = np.fromfile(filename, np.dtype("<f"), -1)
    if len(N) == 2:
        ny, nz = N
        nx = len(data) / (ny * nz)
        assert nx == int(
            nx
        ), f"Size of turbulence box ({len(data)}) does not match ny x nz ({ny*nx}), nx={nx}"
        nx = int(nx)
    else:
        nx, ny, nz = N
        assert len(data) == nx * ny * nz, (
            "Size of turbulence box (%d) does not match nx x ny x nz (%d)"
            % (len(data), nx * ny * nz)
        )
    return data.reshape(nx, ny, nz)
