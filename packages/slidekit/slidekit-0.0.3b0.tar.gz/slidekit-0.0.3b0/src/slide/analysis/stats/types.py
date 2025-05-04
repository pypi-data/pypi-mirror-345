"""
slide/analysis/stats/types
~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class StatResult:
    """
    Data class to hold statistical results.

    Attributes:
        p_values (np.ndarray): Enrichment p-values.
        fdrs (np.ndarray): Enrichment FDR-BH values.
        odds_ratios (np.ndarray): Odds ratios.
    """

    p_values: np.ndarray
    fdrs: np.ndarray
    odds_ratios: np.ndarray

    def __post_init__(self):
        # Downcast all statistical arrays to float16 for memory efficiency
        self.p_values = self.p_values.astype(np.float16)
        self.fdrs = self.fdrs.astype(np.float16)
        self.odds_ratios = self.odds_ratios.astype(np.float16)


@dataclass
class WindowInfo:
    """
    Data class to hold information about sliding windows.

    Attributes:
        start (int): Start index of the window.
        end (int): End index of the window.
        center (int): Center index of the window.
        size (int): Size of the window.
    """

    start: int
    end: int
    center: int
    size: int

    def __post_init__(self):
        # Cast window coordinates to 32-bit ints
        self.start = np.int32(self.start)
        self.end = np.int32(self.end)
        self.center = np.int32(self.center)
        self.size = np.int32(self.size)


@dataclass
class SlidingWindowEnrichment:
    """
    Data class to hold the results of sliding window enrichment analysis.

    Attributes:
        input_container (Input1D): Input container with sorted labels.
        annotation (Annotation): Annotation object containing terms and their associated labels.
        results (StatResult): Object containing enrichment p-values.
        windows (List[WindowInfo]): List of sliding window information.
        window_size (int): Size of the sliding window.
    """

    results: StatResult
    windows: List[WindowInfo]
    window_size: int
