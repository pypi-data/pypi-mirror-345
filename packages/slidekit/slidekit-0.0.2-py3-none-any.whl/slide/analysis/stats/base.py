"""
slide/analysis/stats/base
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Any, Dict

import numpy as np
from scipy.sparse import csr_matrix

from slide.analysis.stats.tests import (
    StatResult,
    compute_hypergeom_test,
    compute_poisson_test,
)
from slide.log import log_describe


class Stats:
    def __init__(self, window_matrix: csr_matrix, annotation_matrix: csr_matrix) -> None:
        """
        Initializes the Stats object for vectorized enrichment analysis.

        Args:
            window_matrix (csr_matrix): A sparse matrix representing windows.
            annotation_matrix (csr_matrix): A sparse matrix representing annotations.
        """
        self.window_matrix = window_matrix  # Shape: (num_windows, num_labels)
        self.annotation_matrix = annotation_matrix  # Shape: (num_terms, num_labels)
        self.num_windows, self.num_labels = self.window_matrix.shape
        self.num_terms = self.annotation_matrix.shape[0]
        self.overlap_matrix = (
            self.window_matrix @ self.annotation_matrix.T
        )  # Shape: (num_windows, num_terms)
        self.window_sizes = np.asarray(
            self.window_matrix.sum(axis=1)
        ).ravel()  # Shape: (num_windows,)
        self.term_sizes = np.asarray(
            self.annotation_matrix.sum(axis=1)
        ).ravel()  # Shape: (num_terms,)

    def run(self, test: str = "poisson", null_distribution: str = "input") -> StatResult:
        """
        Run the selected statistical test.

        Args:
            test (str): Statistical test to use ('hypergeom' or 'poisson'). Defaults to 'poisson'.
            null_distribution (str): Null model basis, 'input' or 'annotation'. Defaults to 'input'.

        Returns:
            StatResult: Object containing enrichment p-values.

        Raises:
            ValueError: If an unrecognized test is provided.
        """
        dispatch = {
            "hypergeom": compute_hypergeom_test,
            "poisson": compute_poisson_test,
        }
        try:
            return dispatch[test](self.window_matrix, self.annotation_matrix, null_distribution)
        except KeyError:
            raise ValueError(f"Invalid test '{test}'. Choose from: {list(dispatch)}.")

    def summary(self) -> Dict[str, Any]:
        """
        Summarize key matrix statistics for the Stats object.

        Returns:
            Dict[str, Any]: Summary statistics of the window and annotation matrices.
        """
        sparse_density_window = (
            self.window_matrix.nnz / self.window_matrix.size if self.window_matrix.size > 0 else 0.0
        )
        sparse_density_annotation = (
            self.annotation_matrix.nnz / self.annotation_matrix.size
            if self.annotation_matrix.size > 0
            else 0.0
        )
        return {
            "num_windows": self.num_windows,
            "num_terms": self.num_terms,
            "num_labels": self.num_labels,
            "sparse_density_window": sparse_density_window,
            "sparse_density_annotation": sparse_density_annotation,
        }

    def describe(self) -> None:
        """Print a formatted summary of the Stats object."""
        log_describe("Stats Summary", self.summary(), key_width=30, log_level="warning")
