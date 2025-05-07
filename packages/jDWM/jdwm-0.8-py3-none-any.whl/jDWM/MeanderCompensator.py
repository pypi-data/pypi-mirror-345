"""
This module contains the class MeanderCompensator, which can be used to convert
a static wake from jDWM into a Meander-compensated static wake.
"""

import numpy as np
from jDWM.utilities import wake_width
from .utilities import CustomBaseModel


try:
    trapz_fun = np.trapezoid  # Numpy 2
except AttributeError:
    trapz_fun = np.trapz  # Numpy 1


def kaimal(f, std, L, U_0):
    return 4 * std ** 2 * L / U_0 / (1 + 6 * f * L / U_0) ** (5 / 3)


class MeanderCompensator(CustomBaseModel):
    """
    Base MeanderCompensator object class. Subclasses are:
     - Reinwardt
     - None
    """


class none(MeanderCompensator):
    def meander_std(self, x):
        return 0

    def __call__(self, r_in, x_in, U_in, V_in, widths_in, **kwargs):
        return r_in, x_in, U_in, V_in, widths_in


class Reinwardt(MeanderCompensator):

    def __init__(self,
                 U: float,
                 TI: float,
                 D_rot: float,
                 f_c: float = None,
                 base_std_dev: float = None,
                 **_):
        self.U = U
        self.TI = TI
        self.D_rot = D_rot
        self.f_c = f_c
        self.base_std_dev = base_std_dev

    def update(self, **params):
        super().update(**params)
        self.f_c = self.U / (2 * self.D_rot)  # meandering cut off frequency

        f = np.linspace(0, self.f_c, 10000)
        spec = kaimal(f, self.TI * self.U, 2.7 * 42, self.U)
        self.base_std_dev = np.sqrt(trapz_fun(spec, f))

    def meander_std(self, x):
        """
        The wake center standard deviation is assumed to be proportional to  the
        meandering time.
        Args:
            x (float or 1D array): Downstream distance [nondimensional with
            rotor radius]
        Returns:
            meander_std (float or 1D array): Standard deviation of wake center
            position [nondimensional with rotor radius]
        """
        return 0.8 * self.base_std_dev / self.U * x

    def pdf(self, r, x):
        """
        Returns the pdf of the lateral meandering for a given downstream
        distance and radial position.
        """
        std_nondim = self.meander_std(x)

        pdf = (
            1
            / np.sqrt(2 * np.pi * std_nondim ** 2)
            * np.exp(-0.5 * (r / std_nondim) ** 2)
        )

        pdf = pdf / sum(pdf)
        return pdf

    def __call__(self, r_in, x_in, U_in, V_in, widths_in, **kwargs):
        self.update(**kwargs)

        N = len(r_in)
        U_out = np.empty_like(U_in)
        widths_out = np.empty_like(widths_in)

        r_temp = np.concatenate([-np.flip(r_in), r_in])
        for i, x in enumerate(x_in):
            if x == 0:
                U_out[i, :] = U_in[i, :]
                widths_out[i] = wake_width(r_in, U_out[i, :])
                continue

            U_temp = np.concatenate([np.flip(U_in[i, :]), U_in[i, :]])
            kernel = self.pdf(r_temp, x)

            # Note. 1 is subtracted and added between convolution to allow
            # convolution to work
            U_out[i, :] = np.convolve(U_temp - 1, kernel, mode="same")[N:] + 1

            widths_out[i] = wake_width(r_in, U_out[i, :])

        return r_in, x_in, U_out, V_in, widths_out
