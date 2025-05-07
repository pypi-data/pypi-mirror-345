import numpy as np
from .utilities import CustomBaseModel


class FilterFunction(CustomBaseModel):
    """
    Base FilterFunction object class. Subclasses are:
     - IEC
     - Madsen
     - Keck
    """


class madsen(FilterFunction):
    """
    Subclass of the :py:class:`jDWM.FilterFunctions.FilterFunction` object class.
    Based on the paper by Helge Madsen titled 'Calibration and validation of the
    dynamic wake meandering model for implementation in an aeroelastic code'
    (2010). The filter functions were ripped directly from Figure 6.
    """

    def filter1(self, x):
        if x < 4:
            return x / 4
        elif x >= 4:
            return 1

    def filter2(self, x):
        if x < 4:
            return 0.0625
        elif 4 <= x < 12:
            return 0.025 * x - 0.0375
        elif 12 <= x < 20:
            return 0.00105 * (x - 12) ** 3 + 0.025 * x - 0.0375
        elif x >= 20:
            return 1


class larsen(FilterFunction):
    """
    Subclass of the :py:class:`jDWM.FilterFunctions.FilterFunction` object class.
    Based on the paper by Torben Larsen titled 'Validation of the dynamic wake
    meander model for loads and power production in the Egmond aan Zee wind
    farm' (2013) which presents a recalibration of the
    :py:class:`jDWM.FilterFunctions.madsen` method.

    filter2 is the same as the :py:class:`jDWM.FilterFunctions.madsen` method.
    Data for filter1, and the coupling filter, filter_amb are ripped directly
    from Figure 6.
    """

    def filter1(self, x):
        if x < 8:
            return (x / 8) ** (3 / 2) - np.sin(
                2 * np.pi * (x / 8) ** (3 / 2)
            ) / 2 ** np.pi
        elif x >= 8:
            return 1

    def filter2(self, x):
        if x < 4:
            return 0.0625
        elif 4 <= x < 12:
            return 0.025 * x - 0.0375
        elif 12 <= x < 20:
            return 0.00105 * (x - 12) ** 3 + 0.025 * x - 0.0375
        elif x >= 20:
            return 1

    def filter_amb(self, ti_amb):
        return 0.23 * ti_amb ** (-0.7)


class IEC(FilterFunction):
    """
    Subclass of the :py:class:`jDWM.FilterFunctions.FilterFunction` object class.
    Based on IEC 61400-1 Edition 4 (2019) Annex E.2.
    """

    def filter1(self, x):
        if x < 8:
            return (x / 8) ** (3 / 2) - np.sin(
                2 * np.pi * (x / 8) ** (3 / 2)
            ) / 2 ** np.pi
        elif x >= 8:
            return 1

    def filter2(self, x):
        if x < 4:
            return 0.0625
        elif 4 <= x < 12:
            return 0.025 * x - 0.0375
        elif 12 <= x < 20:
            return 0.00105 * (x - 12) ** 3 + 0.025 * x - 0.0375
        elif x >= 20:
            return 1


class keck(FilterFunction):
    """
    Subclass of the :py:class:`jDWM.FilterFunctions.FilterFunction` object class.
    Based on the paper by Rolf-Erik keck titled 'Two improvements to the dynamic
    wake meandering model: Including the effects of atmospheric shear on wake
    turbulence and incorporating turbulence build-up in a row of wind turbines'
    (2015)
    """

    def filter1(self, x):
        if x < 4:
            return x / 4
        elif x >= 4:
            return 1

    def filter2(self, x):
        if x < 4:
            return 0.035
        elif x >= 4:
            return 1 - 0.965 * np.exp(-0.35 * (x / 2 - 2))
