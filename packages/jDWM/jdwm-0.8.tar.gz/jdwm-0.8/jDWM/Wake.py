import numpy as np
from scipy import interpolate
from collections import deque
from .AxialInductionModel import AxialInductionModel
from .BoundaryCondition import BoundaryCondition
from .EddyViscosityModel import EddyViscosityModel
from .MeanderCompensator import MeanderCompensator
from .Solvers import Solver
from . import utilities


class StaticWake(utilities.CustomBaseModel):
    """
    Class representing a Static Wake, consisting of a single wake particle.
    """

    def __init__(
        self,
        axial_induction_model: AxialInductionModel = "Joukowsky",
        viscosity_model: EddyViscosityModel="madsen",
        boundary_model: BoundaryCondition="madsen",
        meandercompensator: MeanderCompensator="none",
        solver: Solver="implicit",
        **kwargs,
    ):
        subclass = AxialInductionModel.get_subclass(axial_induction_model)
        self.axial_induction_model = subclass(**kwargs)

        subclass = BoundaryCondition.get_subclass(boundary_model)(**kwargs)
        self.boundary_condition = subclass

        subclass = EddyViscosityModel.get_subclass(viscosity_model)(**kwargs)
        self.viscosity_model = subclass

        subclass = MeanderCompensator.get_subclass(meandercompensator)(**kwargs)
        self.meandercompensator = subclass

        subclass = Solver.get_subclass(solver)(**kwargs)
        self.solver = subclass

    def solve(self, Nx=101, x_max=10, **kwargs):
        self.update(**kwargs)

        x = np.linspace(0, x_max, Nx)
        dx = x[1] - x[0]

        r, a = self.axial_induction_model(**kwargs)
        Nr = len(r)

        U = np.ones((Nx, Nr))
        V = np.zeros((Nx, Nr))
        widths = np.zeros(Nx)
        dUdr = np.zeros((Nx, Nr))

        U[0, :], V[0, :] = self.boundary_condition(r, a)
        dr = np.median(np.diff(r))

        widths[0] = utilities.wake_width(r, U[0, :])
        for i in range(Nx - 1):
            visc = self.viscosity_model(x[i], r, U[i, :])
            _U, _V = self.solver.evolve(r, U[i, :], V[i, :], visc, dx, dr)
            U[i + 1, :], V[i + 1, :] = _U, _V
            dUdr[i + 1, :] = np.gradient(_U, dr)
            widths[i + 1] = utilities.wake_width(r, U[i + 1, :])

        r, x, U, V, widths = self.meandercompensator(r, x, U, V, widths)
        return r, x, U, V, widths, dUdr


class Particle(utilities.CustomBaseModel):
    x: float
    y: float
    z: float
    r: np.ndarray
    U: np.ndarray
    V: np.ndarray
    dUdr: np.ndarray = None
    dt: float
    fc: float
    yaw: float = 0
    tilt: float = 0
    alpha: float = None
    dx_min: float = 0.1

    viscosity_model: EddyViscosityModel = None
    solver: Solver = None

    dr: float = None
    u_: float = 0
    v_: float = 0
    w_: float = 0
    dx_acc: float = 0

    def __init__(self, viscosity_model="madsen", solver="implicit", **kwargs):
        super().__init__(**kwargs)
        self.viscosity_model = EddyViscosityModel.get_subclass(viscosity_model)(
            **kwargs
        )
        self.solver = Solver.get_subclass(solver)(**kwargs)

    def update(self, **kwargs):
        super().update(**kwargs)
        wc = self.fc * self.dt * 2 * np.pi
        self.alpha = np.cos(wc) - 1 + np.sqrt(np.cos(wc) ** 2 - 4 * np.cos(wc) + 3)
        self.dr = self.r[1] - self.r[0]
        self.dUdr = np.zeros_like(self.r)

    def evolve(self, u, v, w, dt):
        self.propagate(u, v, w, dt)
        if self.dx_acc > self.dx_min:
            self.evolve_profile(self.dx_acc)
            self.dx_acc = 0

    def evolve_profile(self, dx):

        visc = self.viscosity_model(self.x, self.r, self.U)
        self.U, self.V = self.solver.evolve(self.r, self.U, self.V, visc, dx, self.dr)
        self.dUdr = np.gradient(self.U, self.dr)

    def propagate(self, u, v, w, dt):
        # low pass filter the velocities from ambient wind field
        self.u_ += self.alpha * (u - self.u_)
        self.v_ += self.alpha * (v - self.v_)
        self.w_ += self.alpha * (w - self.w_)

        # Calculate lateral deflection velocity
        if self.yaw == 0:
            u_lat_def = 0
        else:
            # deficit instead of U
            U_ave = 1 - utilities.rotor_area_mean(self.r, self.U)
            u_lat_def = -0.4 * U_ave * np.sin(np.deg2rad(self.yaw))

        # Calculate vertical deflection velocity
        if self.tilt == 0:
            u_vert_def = 0
        else:
            U_ave = 1 - utilities.rotor_area_mean(self.r, self.U)
            u_vert_def = 0.4 * U_ave * np.sin(np.deg2rad(self.tilt))

        # Calculate particle position change
        dx = self.u_ * dt
        # This is likely right, but for the wrong reasons.
        dy = self.v_ * dt + u_lat_def * dx
        dz = self.w_ * dt + u_vert_def * dx

        self.x += dx
        self.y += dy
        self.z += dz

        # accumulated
        self.dx_acc += dx

    @property
    def width(self):
        return utilities.wake_width(self.r, self.U)


class DynamicWake(utilities.CustomBaseModel):
    """
    A dynamic wake class for a single turbine wake.

    Attributes
    ----------
    particles (deque of Particles): The list of wake particles
    attributes (dict): Attributes of this class, and its submodules.

    Submodules
    ----------
    axial_induction_model (AxialInductionModel)
    boundary_condition (BoundaryCondition)

    Methods
    -------
    update(params)
        Updates the attributes of this class and its submodules.
    step(dt)
        Iterates all wake particles by one time step.
    wsp(X, Y, Z)
        Returns the axial wind speed at the given locations.
    """

    dt: float
    fc: float
    TI: float
    x0: float = 0
    y0: float = 0
    z0: float = 0
    max_particles: int = 100
    d_particle: float = 0.2
    dx_min: float = 0.1
    viscosity_model: str = "madsen"
    solver: str = "implicit"

    particles: deque = None
    boundary_particle: Particle = None
    axial_induction_model: AxialInductionModel = None
    boundary_condition: BoundaryCondition = None

    def __init__(self,

                 axial_induction_model="UserInput",
                 boundary_model="madsen",
                 **kwargs):
        super().__init__(**kwargs)
        self.particles = deque(maxlen=self.max_particles)
        subclass = AxialInductionModel.get_subclass(axial_induction_model)(**kwargs)
        self.axial_induction_model = subclass

        subclass = BoundaryCondition.get_subclass(boundary_model)(**kwargs)
        self.boundary_condition = subclass

        self._new_particle(x=self.x0 + self.dx_min)

        self._update_boundary_particle()

    def _update_boundary_particle(self):
        r, a = self.axial_induction_model()
        U, V = self.boundary_condition(r, a)
        if self.boundary_particle is None:
            self.boundary_particle = Particle(
                viscosity_model=self.viscosity_model,
                solver=self.solver,
                x=self.x0,
                y=self.y0,
                z=self.z0,
                r=r,
                U=U,
                V=V,
                dt=self.dt,
                fc=self.fc,
                TI=self.TI,
            )

        else:
            self.boundary_particle.U = U
            self.boundary_particle.V = V

    def _new_particle(self, x=None, yaw=0, tilt=0, **kwargs):
        self.update(**kwargs)
        r, a = self.axial_induction_model()
        U, V = self.boundary_condition(r, a)

        if x is None:
            x = self.x0
        self.particles.appendleft(
            Particle(
                viscosity_model=self.viscosity_model,
                solver=self.solver,
                x=x,
                y=self.y0,
                z=self.z0,
                r=r,
                U=U,
                V=V,
                dt=self.dt,
                fc=self.fc,
                yaw=yaw,
                tilt=tilt,
                TI=self.TI,
            )
        )

    def step(self, wsp_list, yaw=0, tilt=0, **kwargs):
        """
        Iterates the wake by a single time step, dt.
        Args:
            wsp_list (list): list of tuples of 3 components of wind speed at each particle.
            speed for a given location in space.
            yaw (float): yaw angle of the wake-generating turbine (default=0).
            tilt (float): tilt angle of the wake-generating turbine (default=0).
        Returns:
            None
        """
        self._update_boundary_particle()

        if abs(self.particles[0].x - self.x0) > self.d_particle:
            self._new_particle(yaw=yaw, tilt=tilt, **kwargs)

        for particle, (u, v, w) in zip(self.particles, wsp_list):
            particle.evolve(u, v, w, self.dt)

        # Remove particles that overlap longitudinally.
        part_x = [p.x for p in self.particles]
        to_pop = (np.where(np.diff(part_x) < 0)[0])[::-1]

        # Keep removing particles until monotonic.
        while len(to_pop) > 0:
            for i in to_pop:
                self.particles.remove(self.particles[i])

            part_x = [p.x for p in self.particles]
            to_pop = (np.where(np.diff(part_x) < 0)[0])[::-1]

        # # this will delete the cached interpolators
        # self.__dict__.pop('U_interpolator', None)
        # self.__dict__.pop('dUdr_interpolator', None)

    @property
    def U_interpolator(self):
        """Return interpolator for waked wind field."""
        particles = [self.boundary_particle] + list(self.particles)
        part_x = np.array([p.x for p in particles])
        Z = np.vstack([p.U for p in particles])

        # Keep removing particles until monotonic.
        to_pop = (np.where(np.diff(part_x) <= 0)[0])[::-1]
        while len(to_pop) > 0:
            for i in to_pop:
                part_x = np.delete(part_x, i)
                Z = np.delete(Z, i, axis=0)

            to_pop = (np.where(np.diff(part_x) <= 0)[0])[::-1]

        r = self.particles[0].r
        interpolator = interpolate.RegularGridInterpolator(
            (part_x, r), Z, fill_value=1, bounds_error=False
        )
        return interpolator

    @property
    def dUdr_interpolator(self):
        """Return interpolator for radial derivative of waked wind field."""
        particles = [self.boundary_particle] + list(self.particles)
        part_x = np.array([p.x for p in particles])
        Z = np.vstack([p.dUdr for p in particles])

        # Keep removing particles until monotonic.
        to_pop = (np.where(np.diff(part_x) <= 0)[0])[::-1]
        while len(to_pop) > 0:
            for i in to_pop:
                part_x = np.delete(part_x, i)
                Z = np.delete(Z, i, axis=0)

            to_pop = (np.where(np.diff(part_x) <= 0)[0])[::-1]

        r = self.particles[0].r
        interpolator = interpolate.RegularGridInterpolator(
            (part_x, r), Z, fill_value=0, bounds_error=False
        )
        return interpolator

    def wsp(self, X, Y, Z, ignore_boundary_particle=False, gradient=False):
        """
        Returns the wind speed in the free stream direction at a point in space.
        Args:
            x (ndarray): x coordinates [nondimensional] with the same shape as y and z.
            y (ndarray): y coordinates [nondimensional].
            z (ndarray): z coordinates [nondimensional].
        Returns:
            U (ndarray): Wind speed [nondimensional]. U is the same shape as the input coordinate arrays.
        """
        shape = X.shape
        X, Y, Z = X.ravel(), Y.ravel(), Z.ravel()

        particles = list(self.particles)
        if not ignore_boundary_particle:
            particles = [self.boundary_particle] + particles

        part_x = np.array([p.x for p in particles])
        part_y = np.array([p.y for p in particles])
        part_z = np.array([p.z for p in particles])
        r = self.particles[0].r

        X, C = utilities.cart2offcentrecylindrical(X, Y, Z, part_x, part_y, part_z)

        # values to keep
        mask = (C < r.max()) & (part_x.min() < X) & (X < part_x.max())
        U = utilities.masked_interpolation(
            self.U_interpolator, mask, (X, C), fill_value=1
        )

        if gradient:
            dUdr = utilities.masked_interpolation(
                self.dUdr_interpolator, mask, (X, C), fill_value=0
            )
            return U.reshape(shape), dUdr.reshape(shape)

        return U.reshape(shape)
