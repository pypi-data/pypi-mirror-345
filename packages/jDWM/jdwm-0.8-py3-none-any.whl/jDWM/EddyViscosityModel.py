import numpy as np
from pathlib import Path
from . import FilterFunctions
from .utilities import CustomBaseModel, wake_width
from jDWM.utilities import jit


class EddyViscosityModel(CustomBaseModel):
    """
    Base EddyViscosityModel object class. Subclasses are:
     - IEC
     - madsen
     - larsen
     - keck
    """

    def __init__(self, filter=None, **_):
        self.filter = filter  # filter: FilterFunctions.FilterFunction = None


def _madsen_function(x, r, U, TI, k1, k2):
    width = wake_width(r, U)

    if x < 4:
        x1 = x / 4
    else:
        x1 = 1

    if x < 4:
        x2 = 0.0625
    elif 4 <= x < 12:
        x2 = 0.025 * x - 0.0375
    elif 12 <= x < 20:
        x2 = 0.00105 * (x - 12) ** 3 + 0.025 * x - 0.0375
    elif x >= 20:
        x2 = 1

    visc_amb = x1 * k1 * TI
    visc_wake = x2 * k2 * width * (1 - np.min(U))

    return np.ones_like(r) * (visc_wake + visc_amb)


madsen_function = jit(_madsen_function)


class madsen(EddyViscosityModel):
    """
    Subclass of the :py:class:`jDWM.EddyViscosityModel.EddyViscosityModel`
    object class. Based on the paper by Helge Madsen titled 'Calibration and
    validation of the dynamic wake meandering model for implementation in an
    aeroelastic code' (2010)
    """

    def __init__(self,
                 TI: float,
                 k1: float = 0.07,
                 k2: float = 0.008, **_):
        self.TI = TI
        self.k1 = k1
        self.k2 = k2
        super().__init__(FilterFunctions.madsen())

    def __call__(self, x, r, U):
        """
        Returns the eddy viscosity at a particular downstream distance, x. The
        eddy viscosity is a component of the momentum equation to be solved.

        Args:
            x (float): Downstream distance, (nondimensional).
            r (1D array): radial position (nondimensional).
            U (1D array): Axial wind speed over the blade (nondimensional).

        Returns:
            viscosity (1D array): Eddy viscosity (nondimensional)
        """
        return madsen_function(x, r, U, self.TI, self.k1, self.k2)


class larsen(EddyViscosityModel):
    """
    Subclass of the :py:class:`jDWM.EddyViscosityModel.EddyViscosityModel`
    object class. Based on the paper by Torben Larsen titled 'Validation of the
    dynamic wake meander model for loads and power production in the Egmond aan
    Zee wind farm' (2013) which presents a recalibration of the
    :py:class:`jDWM.EddyViscosityModel.madsen` method.
    """

    def __init__(self,
                 TI: float,
                 kamb: float = 0.1,
                 k2: float = 0.008,
                 **_):
        super().__init__(FilterFunctions.larsen())
        self.TI = TI
        self.kamb = kamb
        self.k2 = k2

    def __call__(self, x, r, U):
        """
        Returns the eddy viscosity at a particular downstream distance, x. The
        eddy viscosity is a component of the momentum equation to be solved.

        Args:
            x (float): Downstream distance, (nondimensional).
            r (1D array): radial position (nondimensional).
            U (1D array): Axial wind speed over the blade (nondimensional).

        Returns:
            viscosity (1D array): Eddy viscosity (nondimensional)
        """
        width = wake_width(r, U)
        visc_amb = (
            self.filter.filter1(x)
            * self.filter.filter_amb(self.TI)
            * self.kamb
            * self.TI
        )
        visc_wake = self.filter.filter2(x) * self.k2 * width * (1 - np.min(U))

        return np.ones_like(r) * (visc_wake + visc_amb)


class IEC(EddyViscosityModel):
    """
    Subclass of the :py:class:`jDWM.EddyViscosityModel.EddyViscosityModel`
    object class. Based on IEC 61400-1 Edition 4 (2019) Annex E.2.
    """

    TI: float
    k1: float = 0.023
    k2: float = 0.008

    def __init__(self,
                 TI: float,
                 k1: float = 0.023,
                 k2: float = 0.008,
                 **_):
        self.TI = TI
        self.k1 = k1
        self.k2 = k2
        super().__init__(FilterFunctions.IEC())

    def __call__(self, x, r, U):
        """
        Returns the eddy viscosity at a particular downstream distance, x. The
        eddy viscosity is a component of the momentum equation to be solved.

        Args:
            x (float): Downstream distance, (nondimensional).
            r (1D array): radial position (nondimensional).
            U (1D array): Axial wind speed over the blade (nondimensional).

        Returns:
            viscosity (1D array): Eddy viscosity
        """
        width = wake_width(r, U)
        visc_amb = self.filter.filter1(x) * self.k1 * self.TI ** 0.3
        visc_wake = self.filter.filter2(x) * self.k2 * width * (1 - np.min(U))

        return np.ones_like(r) * (visc_wake + visc_amb)


class keck(EddyViscosityModel):
    """
    Subclass of the :py:class:`jDWM.EddyViscosityModel.EddyViscosityModel`
    object class. Based on the paper by Rolf-Erik keck titled 'Two improvements
    to the dynamic wake meandering model: Including the effects of atmospheric
    shear on wake turbulence and incorporating turbulence build-up in a row of
    wind turbines' (2015) and 'Implementation of a mixing length turbulence
    formulation into the dynamic wake meandering model' (2012)
    """

    def __init__(self,
                 TI: float,
                 k1: float = 0.0914,  # from 2012 paper
                 k2: float = 0.0216,  # from 2012 paper,
                 **_):
        self.TI = TI
        self.k1 = k1
        self.k2 = k2
        super().__init__(FilterFunctions.keck())

    def __call__(self, x, r, U):
        """
        Returns the eddy viscosity at a particular downstream distance, x. The
        eddy viscosity is a component of the momentum equation to be solved.

        Args:
            x (float): Downstream distance, (nondimensional).
            r (1D array): radial position (nondimensional).
            U (1D array): Axial wind speed over the blade (nondimensional).

        Returns:
            viscosity (1D array): Eddy viscosity
        """
        dx = r[1] - r[0]
        dudr = np.gradient(U, dx)

        width = wake_width(r, U)
        visc_amb = self.filter.filter1(x) * self.k1 * self.TI
        visc_wake = (
            self.filter.filter2(x)
            * self.k2
            * np.max(
                [width ** 2 * abs(dudr), np.ones_like(r) * width * (1 - np.min(U))],
                axis=0,
            )
        )

        return visc_wake + visc_amb
