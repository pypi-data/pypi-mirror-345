"""Define objects to store initial state/trajectory of a particle.

- :class:`ParticleInitialState` is just here to save the position and
  energy of a particle at the entrance of the linac. Saved as an
  :class:`.ListOfElements` attribute.

- :class:`ParticleFullTrajectory` saves the energy, phase, position of a
  particle along the linac. As a single :class:`ParticleInitialState` can
  lead to several :class:`ParticleFullTrajectory` (according to size of the
  mesh, the solver, etc), :class:`.ParticleFullTrajectory` are stored in
  :class:`.SimulationOutput`.

"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

import lightwin.util.converters as convert
from lightwin.tracewin_utils.interface import particle_initial_state_to_command
from lightwin.util.helper import (
    range_vals_object,
    recursive_getter,
    recursive_items,
)
from lightwin.util.typing import GETTABLE_PARTICLE_T


@dataclass
class ParticleInitialState:
    """Hold the initial energy/phase of a particle, and if it is synchronous.

    It is used for :class:`.ListOfElements` attribute.

    """

    w_kin: float
    phi_abs: float
    z_in: float
    synchronous: bool

    @property
    def tracewin_command(self) -> list[str]:
        """Create the energy and phase arguments for TraceWin command."""
        args = (self.w_kin,)
        _tracewin_command = particle_initial_state_to_command(*args)
        return _tracewin_command


@dataclass
class ParticleFullTrajectory:
    r"""Hold the full energy, phase, etc of a particle.

    It is stored in a :class:`.SimulationOutput`.

    Phase is defined as:

    .. math::
        \phi = \omega_{0,\,\mathrm{bunch}} t

    while in :class:`.Field` it is:

    .. math::
        \phi = \omega_{0,\,\mathrm{rf}} t

    """

    w_kin: np.ndarray | list
    phi_abs: np.ndarray | list
    synchronous: bool
    beam: dict[str, NDArray[np.float64] | float]

    def __post_init__(self):
        """Ensure that LightWin has everything it needs, with proper format."""
        if isinstance(self.phi_abs, list):
            self.phi_abs = np.array(self.phi_abs)

        if isinstance(self.w_kin, list):
            self.w_kin = np.array(self.w_kin)

        self.gamma = convert.energy(self.w_kin, "kin to gamma", **self.beam)
        self.beta: np.ndarray

    def __str__(self) -> str:
        """Show amplitude of phase and energy."""
        out = "\tParticleFullTrajectory:\n"
        out += "\t\t" + range_vals_object(self, "w_kin")
        out += "\t\t" + range_vals_object(self, "phi_abs")
        return out

    @property
    def tracewin_command(self) -> list[str]:
        """Raise an error, this method should be called from InitialPart."""
        raise OSError("This method should not be used from here.")

    def compute_complementary_data(self):
        """Compute some data necessary to do the post-treatment."""
        self.beta = convert.energy(self.gamma, "gamma to beta", **self.beam)

    def has(self, key: str) -> bool:
        """Tell if the required attribute is in this class."""
        return key in recursive_items(vars(self))

    def get(
        self, *keys: GETTABLE_PARTICLE_T, to_deg: bool = False, **kwargs: dict
    ) -> tuple[Any]:
        """Shorthand to get attributes."""
        val = {}
        for key in keys:
            val[key] = []

        for key in keys:
            if not self.has(key):
                val[key] = None
                continue

            val[key] = recursive_getter(key, vars(self), **kwargs)

            if val[key] is not None and to_deg and "phi" in key:
                val[key] = np.rad2deg(val[key])

        out = [val[key] for key in keys]

        if len(out) == 1:
            return out[0]
        return tuple(out)


# def create_rand_particles(e_0_mev):
#     """Create two random particles."""
#     delta_z = 1e-4
#     delta_E = 1e-4

#     rand_1 = Particle(-1.42801442802603928417e-04,
#                       1.66094219207764304258e+01,)
#     rand_2 = Particle(2.21221539793564048182e-03,
#                       1.65923664093018210508e+01,)

#     # rand_1 = Particle(
#     #     random.uniform(0., delta_z * .5),
#     #     random.uniform(e_0_mev,  e_0_mev + delta_E * .5),
#     #     omega0_bunch)

#     # rand_2 = Particle(
#     #     random.uniform(-delta_z * .5, 0.),
#     #     random.uniform(e_0_mev - delta_E * .5, e_0_mev),
#     #     omega0_bunch)

#     return rand_1, rand_2
