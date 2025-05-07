from jDWM.EddyViscosityModel import madsen, _madsen_function
import numpy as np
from jDWM.AxialInductionModel import Joukowsky
from jDWM.BoundaryCondition import none
from jDWM.Solvers import implicit


def test_madsen():
    TI = .1
    x_max = 25
    Nx = 101
    x = np.linspace(0, x_max, Nx)
    dx = x[1] - x[0]

    r, a = Joukowsky(tsr=7, ct=0.5)()
    Nr = len(r)

    U = np.ones((Nx, Nr))
    V = np.zeros((Nx, Nr))

    U[0, :], V[0, :] = none()(r, a)
    dr = np.median(np.diff(r))
    solver = implicit()
    visc_lst = []

    for i in range(Nx - 1):
        visc = madsen(TI)(x[i], r, U[i, :])
        visc_py = _madsen_function(x[i], r, U[i, :], TI, k1=0.07, k2=0.008)
        np.testing.assert_array_equal(visc, visc_py)
        visc_lst.append(visc[0])
        _U, _V = solver.evolve(r, U[i, :], V[i, :], visc, dx, dr)
        U[i + 1, :], V[i + 1, :] = _U, _V
    import matplotlib.pyplot as plt
    if 0:
        plt.plot(x[:-1], visc_lst)
        plt.plot(x[:-1:10], visc_lst[::10], '.')
        plt.show()
        print(np.round(visc_lst[::10], 6).tolist())
    np.testing.assert_array_almost_equal(
        visc_lst[::10],
        [0.000137, 0.004518, 0.007205, 0.00736, 0.007542, 0.007717, 0.007949, 0.008461, 0.009475, 0.009389])
