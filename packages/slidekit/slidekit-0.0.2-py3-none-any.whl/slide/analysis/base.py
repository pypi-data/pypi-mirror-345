"""
slide/analysis/base
~~~~~~~~~~~~~~~~~~~
"""

import os
from multiprocessing import get_context
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from tqdm import tqdm

from slide.analysis.stats.base import Stats
from slide.analysis.stats.types import SlidingWindowEnrichment, StatResult, WindowInfo
from slide.analysis.window import Window
from slide.annotation.base import Annotation
from slide.input.base import Input1D, Input2D
from slide.log import log_describe
from slide.results.base import Results


class Analysis:
    """
    High-level interface for running enrichment analyses with minimal configuration.

    This class ties together a sorted list of gene labels with annotation terms,
    applies a sliding window, and computes enrichment statistics.
    """

    def __init__(
        self,
        input_container: Union[Input1D, Input2D],
        annotation: Annotation,
        window_size: Union[int, List[int], Tuple[int], Set[int], np.ndarray] = 20,
    ):
        """
        Initialize the Analysis object.

        Args:
            input_container (Union[Input1D, Input2D]): Input container with sorted labels.
            annotation (Annotation): Annotation object containing terms and their associated labels.
            window_size (Union[int, List[int], Tuple[int], Set[int], np.ndarray]): Size of the sliding window.
                Can be a single integer or a list/tuple/set of integers. Defaults to 20.

        Raises:
            ValueError: If window_size is not a positive int or a collection of positive ints.
        """
        # Validate window_size to be a positive int or a collection of positive ints
        valid_scalar = isinstance(window_size, int) and window_size > 0
        valid_iterable = isinstance(window_size, (list, tuple, set, np.ndarray)) and all(
            isinstance(w, int) and w > 0 for w in window_size
        )
        if not (valid_scalar or valid_iterable):
            raise ValueError("window_size must be a positive int or a collection of positive ints")
        self.input_container = input_container
        self.labels = self.input_container.get_targets()
        self.annotation = annotation
        self.annotation_dict = self.annotation.to_dict()
        self.window_size = window_size

    def run(
        self,
        test: str = "poisson",
        null_distribution: str = "input",
        max_workers: int = 1,
        start_index: int = 0,
        end_index: Optional[int] = None,
        step_size: int = 1,
    ) -> Results:
        """
        Run the enrichment analysis.

        Args:
            test (str, optional): Statistical test to use ('hypergeom' or 'poisson').
                Defaults to 'poisson'.
            null_distribution (str, optional): Basis for the null model ('input' or 'annotation').
                Defaults to 'input'.
            max_workers (int, optional): Max parallel processes. If > 1 and window_size is iterable,
                uses multiprocessing. Defaults to 1.
            start_index (int, optional): Starting index for analysis. Defaults to 0.
            end_index (Optional[int]): Ending index (exclusive). Defaults to None (end of list).
            step_size (int, optional): Step size between windows, i.e., the stride. Defaults to 1.

        Returns:
            Results: Results object containing the enrichment analysis results.
        """
        if isinstance(self.window_size, (list, tuple, set, np.ndarray)):
            if max_workers > 1:
                ctx = get_context("spawn")
                # Limit max_workers to the number of window sizes and available CPU cores
                max_workers = min(max_workers, len(self.window_size), os.cpu_count())
                results = {}
                # Use multiprocessing to run for each window size
                with ctx.Pool(processes=max_workers) as pool, tqdm(
                    total=len(self.window_size), desc="Running statistical analysis"
                ) as pbar:
                    jobs = []
                    for ws in self.window_size:
                        jobs.append(
                            pool.apply_async(
                                self._run_for_window_size,
                                (
                                    ws,
                                    test,
                                    null_distribution,
                                    start_index,
                                    end_index,
                                    step_size,
                                ),
                            )
                        )
                    # Collect results
                    for ws, job in zip(self.window_size, jobs):
                        results[ws] = job.get()
                        pbar.update(1)
                return Results(
                    results, self.input_container, self.annotation, start_index=start_index
                )
            else:
                # Run sequentially for each window size
                with tqdm(total=len(self.window_size), desc="Running statistical analysis") as pbar:
                    results = {}
                    for ws in self.window_size:
                        results[ws] = self._run_for_window_size(
                            ws, test, null_distribution, start_index, end_index, step_size
                        )
                        pbar.update(1)
                return Results(
                    results, self.input_container, self.annotation, start_index=start_index
                )
        else:
            # Run for a single window size
            return Results(
                {
                    self.window_size: self._run_for_window_size(
                        self.window_size, test, null_distribution, start_index, end_index, step_size
                    )
                },
                self.input_container,
                self.annotation,
                start_index=start_index,
            )

    def _run_for_window_size(
        self,
        window_size: int,
        test: str,
        null_distribution: str,
        start_index: int,
        end_index: Optional[int],
        step_size: int,
    ) -> SlidingWindowEnrichment:
        """
        Run enrichment analysis for a specific window size using a sliced universe.

        Args:
            window_size (int): The window size to use for the analysis.
            test (str): Statistical test to use ('hypergeom' or 'poisson').
            null_distribution (str): Basis for the null model ('input' or 'annotation').
            start_index (int): Starting index for analysis.
            end_index (Optional[int]): Ending index (exclusive).
            step_size (int): Step size between windows, i.e., the stride.

        Returns:
            SlidingWindowEnrichment: Result object containing enrichment results and window metadata.
        """
        # Build windows over the full label universe
        full_labels = self.labels
        window = Window(full_labels, window_size, step_size=step_size)
        full_mat, full_info = window.create_window_matrix()

        # Select only the windows that lie between start_index and end_index
        keep = []
        for row_idx, (s, e, c) in enumerate(full_info):
            if s >= start_index and (end_index is None or e <= end_index):
                keep.append((row_idx, WindowInfo(start=s, end=e, center=c, size=window_size)))

        if not keep:
            empty_results = StatResult(
                p_values=np.array([]), fdrs=np.array([]), odds_ratios=np.array([])
            )
            return SlidingWindowEnrichment(
                results=empty_results, windows=[], window_size=window_size
            )

        # Create a sub-matrix of the full matrix
        rows, windows = zip(*keep)
        # Sub-matrix of just those rows
        mat = full_mat[list(rows), :]
        # Build annotation matrix on the full universe
        ann_mat = self.annotation.to_csr(label_universe=full_labels)

        # Run Stats against that full-background matrix
        stats = Stats(window_matrix=mat, annotation_matrix=ann_mat)
        result = stats.run(test=test, null_distribution=null_distribution)

        return SlidingWindowEnrichment(
            results=result, windows=list(windows), window_size=window_size
        )

    def summary(self) -> Dict[str, Any]:
        """
        Return a dictionary of analysis configuration settings.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration summary of the analysis.
        """
        return {
            "num_labels": len(self.labels),
            "window_size": self.window_size,
            "num_terms": len(self.annotation_dict),
            "window_labels_preview": [self.labels[i] for i in range(min(3, len(self.labels)))]
            + (["..."] if len(self.labels) > 3 else []),
            "annotation_terms_preview": list(self.annotation_dict.keys())[:3]
            + (["..."] if len(self.annotation_dict) > 3 else []),
        }

    def describe(self) -> None:
        """Print a formatted description of the enrichment setup."""
        log_describe("Analysis Summary", self.summary(), key_width=30, log_level="warning")
