"""Provide an easy way to generate :class:`.TransferMatrix`."""

from typing import Any, Callable

import numpy as np

from lightwin.core.transfer_matrix.factory import TransferMatrixFactory
from lightwin.core.transfer_matrix.transfer_matrix import TransferMatrix


class TransferMatrixFactoryEnvelope1D(TransferMatrixFactory):
    """Provide a method for easy creation of :class:`.TransferMatrix`."""

    def _preprocess(
        self, single_elts_results: list[dict[str, Any]]
    ) -> np.ndarray:
        """Preprocess the data given by the :class:`.BeamCalculator`."""
        individual = [
            results["r_zz"][i]
            for results in single_elts_results
            for i in range(results["r_zz"].shape[0])
        ]
        return np.array(individual)

    def run(
        self,
        first_cumulated_transfer_matrix: np.ndarray,
        single_elts_results: list[dict[str, Any]],
        element_to_index: Callable,
    ) -> TransferMatrix:
        """Create the transfer matrix from a simulation.

        Parameters
        ----------
        first_cumulated_transfer_matrix : numpy.ndarray
            Cumulated transfer matrix at beginning of :class:`.ListOfElements`
            under study.
        single_elts_results : list[dict[str, Any]]
            Results of the solver.

        Returns
        -------
        TransferMatrix
            Holds all cumulated transfer matrices in all the planes.

        """
        first_cumulated_transfer_matrix = first_cumulated_transfer_matrix[
            4:, 4:
        ]

        individual = self._preprocess(single_elts_results)
        transfer_matrix = TransferMatrix(
            individual=individual,
            first_cumulated_transfer_matrix=first_cumulated_transfer_matrix,
            is_3d=self.is_3d,
            element_to_index=element_to_index,
        )
        return transfer_matrix
