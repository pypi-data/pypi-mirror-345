"""Define a class to store outputs from different :class:`.BeamCalculator`.

.. todo::
    Do I really need the `r_zz_elt` key??

.. todo::
    Do I really need z_abs? Envelope1D does not uses it while TraceWin does.

.. todo::
    Transfer matrices are stored in :class:`.TransferMatrix`, but also in
    ``BeamParameters.zdelta``.

.. todo::
    Maybe the synchronous phase model should appear somewhere in here?

"""

import logging
import math
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Self

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from lightwin.core.beam_parameters.beam_parameters import BeamParameters
from lightwin.core.elements.element import Element
from lightwin.core.list_of_elements.list_of_elements import ListOfElements
from lightwin.core.particle import ParticleFullTrajectory
from lightwin.core.transfer_matrix.transfer_matrix import TransferMatrix
from lightwin.failures.set_of_cavity_settings import SetOfCavitySettings
from lightwin.util.dicts_output import markdown
from lightwin.util.helper import (
    flatten,
    range_vals,
    recursive_getter,
    recursive_items,
)
from lightwin.util.pickling import MyPickler
from lightwin.util.typing import GETTABLE_SIMULATION_OUTPUT_T


@dataclass
class SimulationOutput:
    """Store the information produced by a :class:`.BeamCalculator`.

    Used for fitting, post-processing, plotting.

    Parameters
    ----------
    out_folder :
        Results folder used by the :class:`.BeamCalculator` that created this.
    is_multiparticle :
        Tells if the simulation is a multiparticle simulation.
    is_3d :
        Tells if the simulation is in 3D.
    synch_trajectory :
        Holds energy, phase of the synchronous particle.
    cav_params :
        Holds amplitude, synchronous phase, absolute phase, relative phase of
        cavities.
    beam_parameters :
        Holds emittance, Twiss parameters, envelopes in the various phase
        spaces.
    element_to_index :
        Takes an :class:`.Element`, its name, 'first' or 'last' as argument,
        and returns corresponding index. Index should be the same in all the
        arrays attributes of this class: ``z_abs``, ``beam_parameters``
        attributes, etc.  Used to easily `get` the desired properties at the
        proper position.
    set_of_cavity_settings :
        The cavity parameters used for the simulation.
    transfer_matrix :
         Holds absolute and relative transfer matrices in all planes.
    z_abs :
        Absolute position in the linac in m. The default is None.
    in_tw_fashion :
        A way to output the :class:`.SimulationOutput` in the same way as the
        ``Data`` tab of TraceWin. The default is None.
    r_zz_elt :
        Cumulated transfer matrices in the [z-delta] plane. The default is
        None.

    """

    out_folder: Path
    is_multiparticle: bool
    is_3d: bool

    synch_trajectory: ParticleFullTrajectory

    cav_params: dict[str, float | None] | None

    beam_parameters: BeamParameters

    element_to_index: Callable[[str | Element, str | None], int | slice] | None
    set_of_cavity_settings: SetOfCavitySettings

    transfer_matrix: TransferMatrix | None = None
    z_abs: np.ndarray | None = None
    in_tw_fashion: pd.DataFrame | None = None
    r_zz_elt: list[np.ndarray] | None = None

    def __post_init__(self) -> None:
        """Save complementary data, such as :class:`.Element` indexes."""
        self.elt_idx: list[int]
        if self.cav_params is None:
            logging.error(
                "Failed to init SimulationOutput.elt_idx as .cav_params was "
                "not provided."
            )
        else:
            self.elt_idx = [
                i for i, _ in enumerate(self.cav_params["v_cav_mv"], start=1)
            ]
        self.out_path: Path

    def __str__(self) -> str:
        """Give a resume of the data that is stored."""
        out = "SimulationOutput:\n"
        out += "\t" + range_vals("z_abs", self.z_abs)
        out += self.synch_trajectory.__str__()
        out += self.beam_parameters.__str__()
        return out

    def __repr__(self) -> str:
        """Return str, in order have more concise info."""
        return self.__str__()

    @property
    def beam_calculator_information(self) -> Path:
        """Use ``out_path`` to retrieve info on :class:`.BeamCalculator`."""
        if not hasattr(self, "out_path"):
            return self.out_folder
        return self.out_path.absolute().parents[1]

    def has(self, key: str) -> bool:
        """Tell if the required attribute is in this class.

        We also call the :meth:`.InitialBeamParameters.has`, as it is designed
        to handle the alias (such as ``twiss_zdelta`` <=> ``zdelta.twiss``).

        """
        return (
            key in recursive_items(vars(self))
            or self.beam_parameters.has(key)
            or self.transfer_matrix.has(key)
        )

    def get(
        self,
        *keys: GETTABLE_SIMULATION_OUTPUT_T,
        to_numpy: bool = True,
        to_deg: bool = False,
        elt: (
            Element | str | Collection[Element] | Collection[str] | None
        ) = None,
        pos: Literal["in", "out"] | None = None,
        none_to_nan: bool = False,
        **kwargs: str | bool | None,
    ) -> Any:
        """Get attributes from this class or its attributes.

        Parameters
        ----------
        *keys :
            Name of the desired attributes.
        to_numpy :
            If you want the list output to be converted to a
            :class:`numpy.array`.
        to_deg :
            To convert entries with ``"phi"`` in their name to degrees.
        elt :
            If provided, return the attributes only at the considered
            element(s).
        pos :
            If you want the attribute at the entry, exit, or in the whole
            element.
        none_to_nan :
            To convert ``None`` to ``numpy.nan``.
        **kwargs :
            Other arguments passed to recursive getter.

        Returns
        -------
        out : Any
            Attribute(s) value(s).

        """
        if not isinstance(elt, str) and isinstance(elt, Collection):
            out = [
                self.get(
                    *keys,
                    to_numpy=to_numpy,
                    to_deg=to_deg,
                    elt=x,
                    pos=pos,
                    none_to_nan=none_to_nan,
                    **kwargs,
                )
                for x in elt
            ]
            return list(flatten(out))
        val = {key: [] for key in keys}

        for key in keys:
            if not self.has(key):
                val[key] = None
                continue

            if "r_" in key and "mismatch_factor_" not in key:
                val[key] = self.transfer_matrix.get(
                    key, elt=elt, pos=pos, to_numpy=False, **kwargs
                )
                continue

            val[key] = recursive_getter(
                key, vars(self), to_numpy=False, **kwargs
            )

            if val[key] is None:
                continue

            if to_deg and "phi" in key:
                val[key] = _to_deg(val[key])

            if not to_numpy and isinstance(val[key], np.ndarray):
                val[key] = val[key].tolist()

            if None not in (self.element_to_index, elt):
                return_elt_idx = False
                if key in ("v_cav_mv", "phi_s"):
                    return_elt_idx = True
                idx = self.element_to_index(
                    elt=elt, pos=pos, return_elt_idx=return_elt_idx
                )
                val[key] = val[key][idx]

        out = [
            (
                np.array(val[key])
                if to_numpy and not isinstance(val[key], str)
                else val[key]
            )
            for key in keys
        ]

        if none_to_nan:
            if not to_numpy:
                logging.error(
                    f"{none_to_nan = } while {to_numpy = }, which is not "
                    "supported."
                )
            out = [val.astype(float) for val in out]

        if len(out) == 1:
            return out[0]
        return tuple(out)

    def compute_complementary_data(
        self,
        elts: ListOfElements,
        ref_simulation_output: Self | None = None,
    ) -> None:
        """Compute some other indirect quantities.

        .. todo::
            Fix output_data_in_tw_fashion

        Parameters
        ----------
        elts :
            Must be a full :class:`.ListOfElements`, containing all the
            elements of the linac.
        ref_simulation_output :
            For calculation of mismatch factors. The default is None, in which
            case the calculation is simply skipped.

        """
        if self.z_abs is None:
            self.z_abs = elts.get("abs_mesh", remove_first=True)
        self.synch_trajectory.compute_complementary_data()

        # self.in_tw_fashion = tracewin.interface.output_data_in_tw_fashion()
        if ref_simulation_output is None:
            return

        mismatch_kw = {
            "raise_missing_phase_space_error": True,
            "raise_missing_mismatch_error": True,
            "raise_missing_twiss_error": True,
        }

        phase_space_names = ("zdelta",)
        if self.is_3d:
            phase_space_names = ("zdelta", "x", "y", "t")
        # if self.is_multiparticle:
        #     phase_space_names = ('zdelta', 'x', 'y', 't',
        #                          'x99', 'y99', 'phiw99')

        beam_parameters = self.beam_parameters
        reference_beam_parameters = ref_simulation_output.beam_parameters
        beam_parameters.set_mismatches(
            reference_beam_parameters, *phase_space_names, **mismatch_kw
        )

    def pickle(
        self, pickler: MyPickler, path: Path | str | None = None
    ) -> Path:
        """Pickle (save) the object.

        This is useful for debug and temporary saves; do not use it for long
        time saving.

        """
        if path is None:
            path = self.out_path / "simulation_output.pkl"
        assert isinstance(path, Path)
        pickler.pickle(self, path)

        if isinstance(path, str):
            path = Path(path)
        return path

    @classmethod
    def from_pickle(cls, pickler: MyPickler, path: Path | str) -> Self:
        """Instantiate object from previously pickled file."""
        simulation_output = pickler.unpickle(path)
        return simulation_output  # type: ignore

    def plot(
        self, key: str, to_deg: bool = True, grid: bool = True, **kwargs
    ) -> Axes | np.ndarray:
        """Plot the key."""
        x_axis = markdown["z_abs"]
        df = pd.DataFrame(
            {
                x_axis: self.z_abs,
                markdown[key]: self.get(key, to_deg=to_deg, **kwargs),
            }
        )
        return df.plot(x=x_axis, grid=grid, ylabel=markdown[key], **kwargs)


def _to_deg(
    val: np.ndarray | list | float | None,
) -> np.ndarray | list | float | None:
    """Convert the ``val[key]`` into deg if it is not None."""
    if val is None:
        return None
    if isinstance(val, list):
        return [
            math.degrees(angle) if angle is not None else None for angle in val
        ]
    return np.rad2deg(val)
