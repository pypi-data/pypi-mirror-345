"""
slide/results/base
~~~~~~~~~~~~~~~~~~
"""

import warnings
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

from slide.analysis.stats.types import SlidingWindowEnrichment
from slide.annotation.base import Annotation
from slide.input.base import Input1D, Input2D
from slide.log import log_describe, log_header, logger
from slide.results.cluster import cluster_enrichment_profiles

COLUMN_NAMES = {
    "term": "Term",
    "window_center": "Window Center",
    "abs_window_center": "Abs. Window Center",
    "window_size": "Window Size",
    "p_value": "P-Value",
    "local_fdr": "Local FDR",
    "global_fdr": "Global FDR",
    "sig_score": "Sig. Score",
    "odds_ratio": "Odds Ratio",
}


class Results:
    """
    Encapsulates postprocessing and filtering of enrichment results.

    This class provides methods to filter results based on p-values and FDR,
    cluster terms based on label overlap, and summarize the results.
    """

    def __init__(
        self,
        data: Dict[int, SlidingWindowEnrichment],
        input_container: Union[Input1D, Input2D],
        annotation: Annotation,
        start_index: int = 0,
    ):
        """
        Initialize a Results object with enrichment results.

        Args:
            data (Dict[int, SlidingWindowEnrichment]): Mapping from window center to SlidingWindowEnrichment.
            annotation (Annotation): Annotation for terms.
            start_index (int, optional): The starting index of the analysis relative to the full ranked input.
                Defaults to 0.
        """
        self._data = data
        self._input_container = input_container
        self._start_index = start_index
        self._result_store = ResultStore(
            stat_results=data,
            term_names=list(annotation.to_dict().keys()),
            start_index=start_index,
        )
        self._filtered_entries = None
        self._clusters = None
        self._filter_state: Dict[str, Any] = {
            "max_p_value": 1.0,
            "max_local_fdr": 1.0,
            "max_global_fdr": 1.0,
        }

    def filter(
        self,
        max_p_value: float = 0.05,
        max_local_fdr: float = 1.0,
        max_global_fdr: float = 1.0,
        suppress_log: bool = False,
    ) -> "Results":
        """
        Filter the result DataFrame by p-value, FDR, and optional window indices.

        Args:
            max_p_value (float): Maximum p-value threshold. Defaults to 0.05.
            max_local_fdr (float): Maximum FDR threshold computed per window. Defaults to 1.0.
            max_global_fdr (float): Maximum FDR threshold computed across all windows. Defaults to 1.0.
            suppress_log (bool): Suppress logging of filter parameters. Defaults to False.

        Returns:
            Results: Self after filtering.

        Raises:
            ValueError: If max_p_value is not between 0 and 1.
            ValueError: If max_fdr is not between 0 and 1.
        """
        # Check user input
        if max_p_value < 0.0 or max_p_value > 1.0:
            raise ValueError("P-value threshold must be between 0 and 1.")
        if max_local_fdr is not None and (max_local_fdr < 0.0 or max_local_fdr > 1.0):
            raise ValueError("FDR threshold must be between 0 and 1.")
        if max_global_fdr is not None and (max_global_fdr < 0.0 or max_global_fdr > 1.0):
            raise ValueError("FDR threshold must be between 0 and 1.")

        # Log the filtering parameters
        if not suppress_log:
            log_header("Filtering results", log_level="info")
            logger.info(f"Max P-value: {max_p_value}")
            logger.info(f"Max Local FDR: {max_local_fdr}")
            logger.info(f"Max Global FDR: {max_global_fdr}")

        # Set filter state and create filtered entries
        self._filter_state = {
            "max_p_value": max_p_value,
            "max_local_fdr": max_local_fdr,
            "max_global_fdr": max_global_fdr,
        }
        self._filtered_entries = FilteredEntries(
            self._result_store, self._filter_state, self._input_container.get_targets()
        )

        # Reset clusters when filter is called
        self._clusters = None

        return self

    def cluster(
        self,
        linkage_method: str = "single",
        linkage_metric: str = "jaccard",
        linkage_threshold: Union[float, str] = "auto",
    ) -> "Results":
        """
        Cluster filtered terms based on label overlap or co-occurrence.

        Args:
            linkage_method (str): Linkage method to use ('single', 'complete', etc.).
            linkage_metric (str): Distance metric to use.
            linkage_threshold (Union[float, str]): Threshold to apply clustering. Can be 'auto'.

        Returns:
            Results: Self after clustering.
        """
        # First, fetch the filtered DataFrame
        df_filtered = self._filtered_entries.df
        if df_filtered.empty:
            warnings.warn("Clustering skipped — no filtered results to cluster.")
            return self

        # Pivot DataFrame to get enrichment profile per term
        enrichment_matrix = df_filtered.pivot_table(
            index="Term", columns="Window Center", values="Enrichment", fill_value=0.0
        )
        if enrichment_matrix.shape[0] < 2:
            warnings.warn("Too few terms to cluster. Skipping.")
            return self

        # Perform clustering
        cluster_series = cluster_enrichment_profiles(
            enrichment_df=enrichment_matrix,
            method=linkage_method,
            metric=linkage_metric,
            threshold=linkage_threshold,
            criterion="distance",
        )
        # Group terms by cluster ID
        clusters = {}
        for cluster_id in sorted(cluster_series.unique()):
            # Naturally produces np.int32, so convert to standard int for simpler dict keys
            key = np.int32(cluster_id)
            clusters[key] = cluster_series[cluster_series == cluster_id].index.tolist()
        if not clusters:
            warnings.warn("No valid clusters found after filtering.")

        # Assign clusters
        self._clusters = clusters

        return self

    def summary(self) -> Dict[str, Any]:
        """
        Return structured summary statistics of the filtered results.

        Returns:
            Dict[str, Any]: Summary of the result object.
        """
        # Ensure filtered entries are available
        self._ensure_filtered()
        filtered_df = self._filtered_entries.df

        # Flatten filter state into top-level keys
        flat_filter = {
            "max_p_value": self._filter_state["max_p_value"],
            "max_local_fdr": self._filter_state["max_local_fdr"],
            "max_global_fdr": self._filter_state["max_global_fdr"],
        }

        return {
            "total_results": len(self._data),
            "filtered_results": len(filtered_df),
            "num_terms": filtered_df["Term"].nunique(),
            "num_windows": filtered_df["Window Center"].nunique(),
            **flat_filter,
            "odds_ratio_summary": (
                filtered_df["Odds Ratio"].describe().to_dict()
                if not filtered_df["Odds Ratio"].isna().all()
                else "Not defined for this test (only computed for hypergeometric)"
            ),
            "clusters": len(self._clusters) if self._clusters else 0,
            "sample_terms": filtered_df["Term"].unique().tolist()[:3],
            "sample_clusters": list(self._clusters.items())[:1] if self._clusters else [],
        }

    def describe(self) -> None:
        """Print a human-readable summary of the results."""
        # Pass a flattened filter state to log_describe
        summary = self.summary()
        log_describe("Results Summary", summary, key_width=30, log_level="warning")

    @property
    def df(self) -> pd.DataFrame:
        """
        Access the currently filtered DataFrame.

        Returns:
            pd.DataFrame: Filtered enrichment results.
        """
        # Ensure filtered entries are available
        self._ensure_filtered()
        self._filtered_entries = FilteredEntries(
            self._result_store, self._filter_state, self._input_container.get_targets()
        )
        return self._filtered_entries.df

    @property
    def label_df(self) -> pd.DataFrame:
        """
        Access the driver-gene scores for the current filter.

        Returns:
            pd.DataFrame: DataFrame containing driver-label scores.

        Raises:
            RuntimeError: If the filter has not been applied before accessing this property.
        """
        self._ensure_filtered()
        return self._filtered_entries.label_df

    @property
    def clusters(self) -> Optional[Dict[int, List[str]]]:
        """
        Return clusters, if computed.

        Returns:
            Optional[Dict[int, List[str]]]: Clustered terms by group ID.
        """
        return self._clusters

    def _ensure_filtered(self):
        """Ensure filtered entries exist, applying default filter if not."""
        if self._filtered_entries is None:
            self.filter(
                max_p_value=0.05,
                max_local_fdr=1.0,
                max_global_fdr=1.0,
                suppress_log=True,
            )
            logger.warning(
                "No filter applied. Using default: p ≤ 0.05, Local FDR ≤ 1.0, Global FDR ≤ 1.0."
            )


class ResultStore:
    """
    Encapsulates the storage and retrieval of enrichment results.

    This class provides methods to access and filter results based on p-values and FDR.
    """

    def __init__(
        self,
        stat_results: Dict[int, SlidingWindowEnrichment],
        term_names: List[str],
        start_index: int = 0,
    ):
        """
        Initialize a ResultStore object with enrichment results.

        Args:
            stat_results (Dict[int, SlidingWindowEnrichment]): Mapping from window center to SlidingWindowEnrichment.
            term_names (List[str]): List of term names.
            start_index (int, optional): The starting index of the analysis relative to the full ranked input.
        """
        self.windows = np.array(sorted(stat_results.keys()), dtype=np.int32)
        self.terms = np.array(term_names)
        self._results = stat_results
        self.start_index = start_index
        # All of the NumPy stacking, BH correction, and broadcasting
        # happens inside this private method, which returns a 10‑element tuple:
        (
            self.centers2d,
            self.sizes2d,
            self.pvals2d,
            self.fdr2d,
            self.fdr_global2d,
            self.scores2d,
            self.odds2d,
        ) = self._precompute_master_arrays()

    def _precompute_master_arrays(self) -> Tuple[np.ndarray, ...]:
        """
        Precompute master arrays for enrichment results.

        Returns:
            Tuple[np.ndarray, ...]: A tuple of precomputed arrays containing enrichment results.

        Raises:
            ValueError: If there are no results to process.
        """
        # Check if results are empty, if so return empty arrays
        if not self._results:
            raise ValueError("No results to process.")

        # Stack enrichment p-values into (W, T) arrays
        pvals2d = np.vstack(
            [self._results[w].results.p_values.astype(np.float16) for w in self.windows]
        )
        # Determine total number of window rows and term count
        total_rows, T = pvals2d.shape
        # Local FDR (fill missing with ones)
        fdr2d = np.vstack(
            [
                (
                    self._results[w].results.fdrs.astype(np.float16)
                    if self._results[w].results.fdrs is not None
                    else np.ones(T)
                )
                for w in self.windows
            ]
        )

        # Compute global FDR and significance scores
        flat_pvals = pvals2d.ravel()
        if flat_pvals.size == 0:
            fdr_global2d = np.zeros_like(pvals2d)
            scores2d = np.zeros_like(pvals2d)
        else:
            _, flat_egfdr, _, _ = multipletests(flat_pvals, method="fdr_bh")
            fdr_global2d = flat_egfdr.astype(np.float16).reshape(total_rows, T)
            with np.errstate(divide="ignore"):
                # Uses global FDR for significance score
                flat_esig_score = -np.log10(flat_pvals**0.5 * flat_egfdr**2)
            scores2d = flat_esig_score.reshape(total_rows, T).astype(np.float16)

        # Window coordinates for each individual window row
        starts_1d = np.concatenate(
            [[win.start for win in self._results[w].windows] for w in self.windows]
        ).astype(np.int32)
        ends_1d = np.concatenate(
            [[win.end for win in self._results[w].windows] for w in self.windows]
        ).astype(np.int32)
        sizes_1d = np.concatenate(
            [[win.size for win in self._results[w].windows] for w in self.windows]
        ).astype(np.int32)

        # Broadcast to (total_rows, T)
        starts2d = np.repeat(starts_1d[:, None], T, axis=1)
        ends2d = np.repeat(ends_1d[:, None], T, axis=1)
        sizes2d = np.repeat(sizes_1d[:, None], T, axis=1)
        centers2d = ((starts2d + ends2d) // 2).astype(np.int32)
        # Apply window size correction to significance scores; only normalize if shapes match
        if scores2d.shape == sizes2d.shape and scores2d.size > 0:
            with np.errstate(divide="ignore"):
                scores2d /= np.log1p(sizes2d)
        else:
            warnings.warn(
                f"Skipping window-size normalization: scores2d shape {scores2d.shape} "
                f"does not match sizes2d shape {sizes2d.shape}"
            )
        # Odds ratio
        odds2d = np.vstack(
            [self._results[w].results.odds_ratios.astype(np.float16) for w in self.windows]
        )

        return (
            centers2d,
            sizes2d,
            pvals2d,
            fdr2d,
            fdr_global2d,
            scores2d,
            odds2d,
        )

    def get_filtered_arrays(
        self,
        pval_thresh: float,
        local_fdr_thresh: Optional[float] = None,
        global_fdr_thresh: Optional[float] = None,
    ) -> Generator[Tuple[np.ndarray, ...], None, None]:
        """
        Yield filtered arrays based on p-value, local FDR, and global FDR.

        Args:
            pval_thresh (float): P-value threshold.
            local_fdr_thresh (Optional[float]): Local FDR threshold.
            global_fdr_thresh (Optional[float]): Global FDR threshold.

        Yields:
            Tuple[np.ndarray, ...]: A tuple of arrays containing filtered results.
        """
        # Check if there are any results to filter
        if self.pvals2d.size == 0:
            yield from ()
            return

        # Apply a mask to filter results
        mask = self.pvals2d > 0
        mask &= self.pvals2d <= pval_thresh
        if local_fdr_thresh is not None:
            mask &= self.fdr2d <= local_fdr_thresh
        if global_fdr_thresh is not None:
            mask &= self.fdr_global2d <= global_fdr_thresh
        # Extract indices of valid results
        win_idx, term_idx = np.nonzero(mask)

        yield (
            self.terms[term_idx],
            self.centers2d[win_idx, term_idx],
            self.sizes2d[win_idx, term_idx],
            self.pvals2d[win_idx, term_idx],
            self.fdr2d[win_idx, term_idx],
            self.fdr_global2d[win_idx, term_idx],
            self.scores2d[win_idx, term_idx],
            self.odds2d[win_idx, term_idx],
        )


class FilteredEntries:
    """
    Encapsulates filtered enrichment results.

    This class provides a cached DataFrame of filtered results based on user-defined criteria.
    """

    def __init__(
        self,
        result_store: ResultStore,
        filter_state: Dict[str, Any],
        targets: Sequence[str],
    ):
        """
        Initialize a FilteredEntries object with a ResultStore and filter state.

        Args:
            result_store (ResultStore): The ResultStore object containing enrichment results.
            filter_state (Dict[str, Any]): The current filter state.
            targets (Sequence[str]): The list of label targets.
        """
        self.result_store = result_store
        self.filter_state = filter_state
        self._targets = targets
        self._label_df_cache = None
        self._cached_df = None

    @property
    def df(self) -> pd.DataFrame:
        """
        Return the filtered DataFrame, computing it on first access and caching thereafter.

        Returns:
            pd.DataFrame: Filtered DataFrame containing enrichment results.
        """
        # Return cached DataFrame if available
        if self._cached_df is not None:
            return self._cached_df

        # Define column ordering to match legacy output, but insert Abs. Window Center after Window Center
        cols = [
            COLUMN_NAMES["term"],
            COLUMN_NAMES["window_center"],
            COLUMN_NAMES["abs_window_center"],
            COLUMN_NAMES["window_size"],
            COLUMN_NAMES["p_value"],
            COLUMN_NAMES["local_fdr"],
            COLUMN_NAMES["global_fdr"],
            COLUMN_NAMES["sig_score"],
            COLUMN_NAMES["odds_ratio"],
        ]
        # Accumulate each chunk as its own small DataFrame
        dfs: list[pd.DataFrame] = []
        for (
            term_arr,
            center_arr,
            size_arr,
            p_arr,
            lfdr_arr,
            gfdr_arr,
            score_arr,
            or_arr,
        ) in self.result_store.get_filtered_arrays(
            pval_thresh=self.filter_state["max_p_value"],
            local_fdr_thresh=self.filter_state["max_local_fdr"],
            global_fdr_thresh=self.filter_state["max_global_fdr"],
        ):
            # Compute absolute window center
            abs_center_arr = center_arr + self.result_store.start_index
            # Build a temporary DataFrame for this batch of arrays
            dfs.append(
                pd.DataFrame(
                    {
                        cols[0]: term_arr,
                        cols[1]: center_arr,
                        cols[2]: abs_center_arr,
                        cols[3]: size_arr,
                        cols[4]: p_arr,
                        cols[5]: lfdr_arr,
                        cols[6]: gfdr_arr,
                        cols[7]: score_arr,
                        cols[8]: or_arr,
                    }
                )
            )

        # If we got any data, concatenate into one DataFrame; otherwise create empty
        if dfs:
            # Single concat avoids multiple large intermediate copies
            self._cached_df = pd.concat(dfs, ignore_index=True)
            # Set categorical dtype for term column for memory efficiency
            self._cached_df[cols[0]] = self._cached_df[cols[0]].astype("category")
            # Downcast integers and floats to 32-bit
            for num_col in cols[1:4]:
                self._cached_df[num_col] = self._cached_df[num_col].astype(np.int32)
            for num_col in cols[4:]:
                self._cached_df[num_col] = self._cached_df[num_col].astype(np.float32)
        else:
            # No entries passed the filters: return empty DataFrame with correct columns
            self._cached_df = pd.DataFrame(columns=cols)

        # Sort by Window Center (ascending), then by Sig. Score (descending) within each window
        self._cached_df.sort_values(
            by=[COLUMN_NAMES["window_center"], COLUMN_NAMES["sig_score"]],
            ascending=[True, False],
            inplace=True,
        )

        return self._cached_df

    @property
    def label_df(self) -> pd.DataFrame:
        """
        Return the driver-label scores for the current filter.

        Returns:
            pd.DataFrame: DataFrame containing driver-label scores.
        """
        # Check if the label DataFrame is already cached
        if self._label_df_cache is None:
            # Compute the scores and create a DataFrame
            scores = self._fast_driver_label_scoring(self.df, self._targets)
            df_label = pd.DataFrame(
                {
                    "Label Index": np.arange(len(self._targets), dtype=int),
                    "Label": self._targets,
                    "Score Sum": scores,
                }
            )
            # Sort then store the DataFrame in cache
            self._label_df_cache = df_label.sort_values("Score Sum", ascending=False).reset_index(
                drop=True
            )

        return self._label_df_cache

    def _fast_driver_label_scoring(
        self, results_df: pd.DataFrame, sorted_labels: Sequence[str]
    ) -> np.ndarray:
        """
        Fast label scoring method for driver labels.

        Args:
            results_df (pd.DataFrame): DataFrame containing enrichment results.
            sorted_labels (Sequence[str]): List of sorted labels.

        Returns:
            np.ndarray: Array of driver label scores.
        """
        # Build a diff-array for the driver label scores
        num_labels = len(sorted_labels)
        diff_array = np.zeros(num_labels + 1, dtype=np.float64)

        # Use the results DataFrame to create a diff-array
        scoring_df = results_df.copy()
        scoring_df["Window Start"] = (
            scoring_df["Window Center"] - (scoring_df["Window Size"] // 2)
        ).clip(lower=0, upper=num_labels - 1)

        scoring_df["Window End"] = (
            scoring_df["Window Center"] + (scoring_df["Window Size"] // 2)
        ).clip(lower=0, upper=num_labels - 1) + 1
        if scoring_df.empty:
            return np.zeros(num_labels, dtype=np.float64)

        # Add the scores to the diff-array
        start_indices = scoring_df["Window Start"].astype(int).to_numpy()
        end_indices = scoring_df["Window End"].astype(int).to_numpy()
        signal_values = scoring_df["Sig. Score"].to_numpy()
        np.add.at(diff_array, start_indices, signal_values)
        np.add.at(diff_array, end_indices, -signal_values)

        # Compute the prefix sum to get the final scores
        return np.cumsum(diff_array[:-1])
