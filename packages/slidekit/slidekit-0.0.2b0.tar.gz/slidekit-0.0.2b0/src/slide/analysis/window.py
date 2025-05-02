"""
slide/analysis/window
~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix

from slide.log import log_describe


class Window:
    """
    Generates sliding windows (sparse adjacency matrices) from a ranked list of labels.

    This class provides methods to create sliding window matrices, calculate coverage,
    and generate summary statistics for the windows.
    """

    def __init__(
        self,
        label_universe: List[str],
        window_size: int,
        step_size: int = 1,
    ):
        """
        Initialize a new Window instance with a fixed window size over a subset of ranked labels.

        Args:
            label_universe (List[str]): A list of ranked labels (e.g., gene names) to be used for windowing.
            window_size (int): The fixed window size to use for all windows.
            step_size (int, optional): The step size between window starts, i.e., the stride.
                Defaults to 1.

        Raises:
            ValueError: If window_size or step_size is not a positive integer.
        """
        # Validate inputs
        if window_size <= 0:
            raise ValueError("window_size must be a positive integer")
        if step_size <= 0:
            raise ValueError("step_size must be a positive integer")
        self.label_universe = label_universe
        self.num_labels = len(self.label_universe)
        self.window_size = window_size
        self.step_size = step_size

    def create_window_matrix(self) -> Tuple[csr_matrix, List[Tuple[int, int, int]]]:
        """
        Create a sparse sliding window matrix using the fixed window size provided at initialization.

        Returns:
            Tuple[csr_matrix, List[Tuple[int, int, int]]]: A tuple of the sparse matrix and a list of tuples
                containing the start, end, and center indices of each window.
        """
        window_size = self.window_size
        num_windows = max(0, (self.num_labels - window_size) // self.step_size + 1)
        window_matrix = lil_matrix((num_windows, self.num_labels), dtype=np.int8)
        window_info = []
        # Create the window matrix and store window information
        for i, start in enumerate(range(0, self.num_labels - window_size + 1, self.step_size)):
            end = start + window_size
            center = (start + end) // 2
            window_matrix[i, start:end] = 1
            window_info.append((start, end, center))

        return window_matrix.tocsr(), window_info

    def to_csr(self) -> csr_matrix:
        """
        Convenience method that returns the CSR matrix using the fixed window size,
        discarding the window metadata.

        Returns:
            csr_matrix: The generated sparse window matrix.
        """
        csr_mat, _ = self.create_window_matrix()
        return csr_mat

    def summary(self) -> Dict[str, Any]:
        """
        Provides summary statistics for the windows generated at the fixed window size.

        Returns:
            Dict[str, Any]: A summary of the window statistics including various statistics.
        """
        _, window_info = self.create_window_matrix()
        num_windows = len(window_info)
        avg_center = (
            np.mean([center for (_, _, center) in window_info]) if num_windows > 0 else None
        )
        coverage = self._get_coverage()
        return {
            "num_windows": num_windows,
            "avg_center": avg_center,
            "window_size": self.window_size,
            "step_size": self.step_size,
            "total_labels": self.num_labels,
            "coverage": coverage,
        }

    def describe(self) -> None:
        """Print a detailed summary of the window configuration."""
        log_describe("Window Summary", self.summary(), key_width=30, log_level="warning")

    def _get_coverage(self) -> float:
        """
        Calculates the fraction of gene indices that appear in at least one window for the fixed window size.

        Returns:
            float: Fraction of gene indices covered.
        """
        _, window_info = self.create_window_matrix()
        covered = set()
        for start, end, _ in window_info:
            covered.update(range(start, end))

        return len(covered) / self.num_labels if self.num_labels > 0 else 0.0
