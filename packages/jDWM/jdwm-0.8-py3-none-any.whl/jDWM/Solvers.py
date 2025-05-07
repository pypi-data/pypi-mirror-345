import numpy as np
from .utilities import CustomBaseModel, Ainslie

from scipy import linalg


class Solver(CustomBaseModel):
    """
    Base Solver object class. Subclasses are:
     - python
     - implicit
     - explicit
    """

    def __init__(self, **_):
        ""


class python(Solver):
    """

    """

    def evolve(self, r, U, V, visc, dx, dr):
        return Ainslie.evolve(r, U, V, visc, dx, dr)


class implicit(Solver):
    """

    """

    def evolve(self, r, U, V, visc, dx, dr):
        return Ainslie.evolve(r, U, V, visc, dx, dr)


class explicit(Solver):
    """

    """

    def evolve(self, r, U, V, visc, dx, dr):
        return Ainslie.evolve_explicit(r, U, V, visc, dx, dr)
