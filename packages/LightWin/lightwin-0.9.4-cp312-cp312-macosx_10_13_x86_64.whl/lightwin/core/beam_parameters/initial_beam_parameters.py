"""Gather beam parameters at the entrance of a :class:`.ListOfElements`.

For a list of the units associated with every parameter, see
:ref:`units-label`.

"""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from lightwin.tracewin_utils.interface import beam_parameters_to_command
from lightwin.util.helper import recursive_items
from lightwin.util.typing import (
    GETTABLE_BEAM_PARAMETERS_T,
    PHASE_SPACE_T,
    PHASE_SPACES,
)

from .phase_space.initial_phase_space_beam_parameters import (
    InitialPhaseSpaceBeamParameters,
)


@dataclass
class InitialBeamParameters:
    r"""
    Hold all emittances, envelopes, etc in various planes at a single position.

    Parameters
    ----------
    z_abs :
        Absolute position in the linac in :unit:`m`.
    gamma_kin :
        Lorentz gamma factor.
    beta_kin :
        Lorentz beta factor.
    zdelta, z, phiw, x, y, t :
        Beam parameters respectively in the :math:`[z-z\delta]`,
        :math:`[z-z']`, :math:`[\phi-W]`, :math:`[x-x']`, :math:`[y-y']` and
        :math:`[t-t']` planes.
    phiw99, x99, y99 :
        99% beam parameters respectively in the :math:`[\phi-W]`,
        :math:`[x-x']` and :math:`[y-y']` planes. Only used with multiparticle
        simulations.

    """

    z_abs: float
    gamma_kin: float
    beta_kin: float

    def __post_init__(self) -> None:
        """Declare the phase spaces without initalizing them."""
        self.zdelta: InitialPhaseSpaceBeamParameters
        self.z: InitialPhaseSpaceBeamParameters
        self.phiw: InitialPhaseSpaceBeamParameters
        self.x: InitialPhaseSpaceBeamParameters
        self.y: InitialPhaseSpaceBeamParameters
        self.t: InitialPhaseSpaceBeamParameters
        self.phiw99: InitialPhaseSpaceBeamParameters
        self.x99: InitialPhaseSpaceBeamParameters
        self.y99: InitialPhaseSpaceBeamParameters

    def __str__(self) -> str:
        """Give compact information on the data that is stored."""
        out = "\tBeamParameters:\n"
        for phase_space_name in PHASE_SPACES:
            if not hasattr(self, phase_space_name):
                continue

            phase_space = getattr(self, phase_space_name)
            out += f"{phase_space}"
        return out

    def has(self, key: str) -> bool:
        """Tell if the required attribute is in this class.

        Notes
        -----
        ``key = 'property_phasespace'`` will return True if ``'property'``
        exists in ``phasespace``. Hence, the following two commands will have
        the same return values:

            .. code-block:: python

                self.has('twiss_zdelta')
                self.zdelta.has('twiss')

        See Also
        --------
        get

        """
        if phase_space_name_hidden_in_key(key):
            key, phase_space_name = separate_var_from_phase_space(key)
            phase_space = getattr(self, phase_space_name)
            return hasattr(phase_space, key)
        return key in recursive_items(vars(self))

    def get(
        self,
        *keys: GETTABLE_BEAM_PARAMETERS_T,
        to_numpy: bool = True,
        none_to_nan: bool = False,
        phase_space_name: PHASE_SPACE_T | None = None,
        **kwargs: Any,
    ) -> Any:
        """Get attributes from this class or its attributes.

        Notes
        -----
        What is particular in this getter is that all
        :class:`.InitialPhaseSpaceBeamParameters` objects have attributes with
        the same name: ``twiss``, ``alpha``, ``beta``, ``gamma``, ``eps``, etc.

        Hence, you must provide either a ``phase_space_name`` argument which
        shall be in :data:`.PHASE_SPACES`, either or you must append the name
        of the phase space to the name of the desired variable with an
        underscore.

        Examples
        --------
        >>> initial_beam_parameters: InitialBeamParameters
        >>> initial_beam_parameters.get("beta", phase_space_name="zdelta")
        >>> initial_beam_parameters.get("beta_zdelta")  # Alternative
        >>> initial_beam_parameters.get("beta")  # Incorrect

        See Also
        --------
        :meth:`has`

        Parameters
        ----------
        *keys :
            Name of the desired attributes.
        to_numpy :
            If you want the list output to be converted to a np.ndarray. The
            default is True.
        none_to_nan :
            To convert ``None`` to ``np.nan``. The default is True.
        phase_space_name :
            Phase space in which you want the key. The default is None. In this
            case, the quantities from the ``zdelta`` phase space are taken.
            Otherwise, it must be in :data:`.PHASE_SPACES`.
        **kwargs: Any
            Other arguments passed to recursive getter.

        Returns
        -------
        out : Any
            Attribute(s) value(s).

        """
        val = {key: [] for key in keys}

        # Explicitely look into a specific (Initial)PhaseSpaceBeamParameters
        if phase_space_name is not None:
            phase_space = getattr(self, phase_space_name)
            val = {key: getattr(phase_space, key) for key in keys}

        else:
            for key in keys:
                if phase_space_name_hidden_in_key(key):
                    short_key, phase_space_name = (
                        separate_var_from_phase_space(key)
                    )
                    assert hasattr(self, phase_space_name), (
                        f"{phase_space_name = } not set for current "
                        "InitialBeamParameters object."
                    )
                    phase_space = getattr(self, phase_space_name)
                    val[key] = getattr(phase_space, short_key)
                    continue

                # Look for key in BeamParameters
                if self.has(key):
                    val[key] = getattr(self, key)
                    continue

                val[key] = None

        out = [val[key] for key in keys]
        if to_numpy:
            out = [
                np.array(val) if isinstance(val, list) else val for val in out
            ]
            if none_to_nan:
                out = [val.astype(float) for val in out]

        if len(out) == 1:
            return out[0]
        return tuple(out)

    @property
    def tracewin_command(self) -> list[str]:
        """Return the proper input beam parameters command."""
        _tracewin_command = self._create_tracewin_command()
        return _tracewin_command

    @property
    def sigma(self) -> np.ndarray:
        """Give value of sigma.

        .. todo::
            Could be cleaner.

        """
        sigma = np.zeros((6, 6))

        sigma_x = np.zeros((2, 2))
        if self.has("x"):
            sigma_x = self.x.sigma

        sigma_y = np.zeros((2, 2))
        if self.has("y"):
            sigma_y = self.y.sigma

        sigma_zdelta = self.zdelta.sigma

        sigma[:2, :2] = sigma_x
        sigma[2:4, 2:4] = sigma_y
        sigma[4:, 4:] = sigma_zdelta
        return sigma

    def _create_tracewin_command(
        self, warn_missing_phase_space: bool = True
    ) -> list[str]:
        """
        Turn emittance, alpha, beta from the proper phase-spaces into command.

        When phase-spaces were not created, we return np.nan which will
        ultimately lead TraceWin to take this data from its ``.ini`` file.

        """
        args = []
        for phase_space_name in ("x", "y", "z"):
            if not self.has(phase_space_name):
                eps, alpha, beta = np.nan, np.nan, np.nan
                phase_spaces_are_needed = self.z_abs > 1e-10
                if warn_missing_phase_space and phase_spaces_are_needed:
                    logging.warning(
                        f"{phase_space_name} phase space not "
                        "defined, keeping default inputs from the "
                        "`.ini.`."
                    )
            else:
                phase_space = getattr(self, phase_space_name)
                eps = phase_space.eps
                alpha = phase_space.alpha
                beta = phase_space.beta

            args.extend((eps, alpha, beta))
        return beam_parameters_to_command(*args)


# =============================================================================
# Private
# =============================================================================
def phase_space_name_hidden_in_key(key: str) -> bool:
    """Look for the name of a phase-space in a key name."""
    if "_" not in key:
        return False

    to_test = key.split("_")
    if to_test[-1] in PHASE_SPACES:
        return True
    return False


def separate_var_from_phase_space(key: str) -> tuple[str, PHASE_SPACE_T]:
    """Separate variable name from phase space name."""
    splitted = key.split("_")
    key = "_".join(splitted[:-1])
    phase_space = splitted[-1]
    assert phase_space in PHASE_SPACES
    return key, phase_space
