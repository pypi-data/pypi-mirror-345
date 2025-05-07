import numpy as np
from pathlib import Path
from .utilities import rotor_area_mean, CustomBaseModel


class BoundaryCondition(CustomBaseModel):
    """
    Base BoundaryCondition object class. Subclasses are:
     - None
     - Madsen
     - Keck
     - IEC
    """

    def _axial_velocity(self, r, a):
        return 1 - 2 * a

    def _radial_velocity(self, r, a):
        return np.zeros_like(r)


class none(BoundaryCondition):
    """
    Subclass of the :py:class:`jDWM.BoundaryCondition.BoundaryCondition` object class.
    """

    def _expand_radius(self, r, a, **kwargs):
        return r

    def __call__(self, r, a, **kwargs):
        self.update(**kwargs)

        r_out = self._expand_radius(r, a)
        U = self._axial_velocity(r, a)
        V = self._radial_velocity(r, a)

        # interpolate U and V onto unexpanded radial locations
        U = np.interp(r, r_out, U)
        V = np.interp(r, r_out, V)
        return U, V


class madsen(BoundaryCondition):
    """
    Subclass of the :py:class:`jDWM.BoundaryCondition.BoundaryCondition` object class.
    """

    def _expand_radius(self, r, a, **kwargs):
        r_out = np.zeros_like(r)
        a_ave = rotor_area_mean(r, a)
        fw = 1 - 0.45 * a_ave ** 2

        r_out[0] = r[0]

        for i in range(len(r) - 1):
            r_out[i + 1] = np.sqrt(
                (1 - a[i]) / (1 - 2 * a[i]) * (r[i + 1] ** 2 - r[i] ** 2)
                + r_out[i] ** 2
            )
        r_out = fw * r_out
        return r_out

    def __call__(self, r, a):

        # Saturation required to prevent complex square roots.
        # As implemented in HAWC2
        a[a >= 0.47] = 0.47
        a[a <= -0.47] = -0.47

        r_out = self._expand_radius(r, a)
        U = self._axial_velocity(r, a)
        V = self._radial_velocity(r, a)

        # interpolate U and V onto unexpanded radial locations
        U = np.interp(r, r_out, U)
        V = np.interp(r, r_out, V)
        return U, V


class keck(BoundaryCondition):
    """
    Subclass of the :py:class:`jDWM.BoundaryCondition.BoundaryCondition` object class.
    """

    def _axial_velocity(self, r, a):
        return 1 - 2.1 * a

    def _expand_radius(self, r, a, **kwargs):
        r_out = np.zeros_like(r)
        a_ave = rotor_area_mean(r, a)
        r_out = r * np.sqrt((1 - a_ave) / (1 - 1.98 * a_ave))
        return r_out

    def __call__(self, r, a, **kwargs):
        self.update(**kwargs)

        r_out = self._expand_radius(r, a)
        U = self._axial_velocity(r, a)
        V = self._radial_velocity(r, a)

        # interpolate U and V onto unexpanded radial locations
        U = np.interp(r, r_out, U)
        V = np.interp(r, r_out, V)
        return U, V


class IEC(BoundaryCondition):
    """
    Subclass of the :py:class:`jDWM.BoundaryCondition.BoundaryCondition` object class.
    """

    def _axial_velocity(self, r, a):
        a_ave = rotor_area_mean(r, a)
        U = np.ones_like(r)
        U[r <= 1] *= 1 - 2 * a_ave
        U[0] = 1
        return U

    def _expand_radius(self, r, a):
        r_out = np.zeros_like(r)
        a_ave = rotor_area_mean(r, a)

        # ct = 4*(a_ave - rotor_area_mean(r, a**2))
        ct = 4 * (1 - a_ave) * a_ave
        m = 1 / np.sqrt(1 - ct)

        r_out = 2 * r * (1 - 0.45 * a_ave ** 2) * np.sqrt((1 + m) / 8)
        return r_out

    def __call__(self, r, a, **kwargs):
        self.update(**kwargs)

        r_out = self._expand_radius(r, a)
        U = self._axial_velocity(r, a)
        V = self._radial_velocity(r, a)

        # interpolate U and V onto unexpanded radial locations
        U = np.interp(r, r_out, U)
        V = np.interp(r, r_out, V)
        return U, V
