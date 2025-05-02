"""
slide/analysis/stats/tests
~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.stats import hypergeom, poisson
from statsmodels.stats.multitest import multipletests

from slide.analysis.stats.types import StatResult


def compute_hypergeom_test(
    windows: csr_matrix,
    annotations: csr_matrix,
    null_distribution: str = "input",
) -> StatResult:
    """
    Compute hypergeometric enrichment p-values.

    Args:
        windows (csr_matrix): Binary matrix of windows x labels.
        annotations (csr_matrix): Binary matrix of terms x labels.
        null_distribution (str): 'input' or 'annotations'.

    Returns:
        StatResult: Enrichment p-value matrices.

    Raises:
        ValueError: If null_distribution is not 'input' or 'annotations'.
    """
    num_labels = windows.shape[1]

    if null_distribution == "input":
        background = num_labels
        row_sums = windows.sum(axis=1).A.flatten()
        col_sums = annotations.sum(axis=1).A.flatten()
    elif null_distribution == "annotations":
        # Filter to labels (columns) that have at least one annotation
        valid_labels = annotations.sum(axis=0).A.flatten() > 0
        annotations = annotations[:, valid_labels]
        windows = windows[:, valid_labels]
        background = int(valid_labels.sum())
        row_sums = windows.sum(axis=1).A.flatten()
        col_sums = annotations.sum(axis=1).A.flatten()
    else:
        raise ValueError("null_distribution must be 'input' or 'annotations'")

    # Convert to 1D arrays
    observed = (windows @ annotations.T).toarray()
    row_sums = row_sums.reshape(-1, 1)
    col_sums = col_sums.reshape(1, -1)
    background = np.array(background).reshape(1, 1)
    # Compute hypergeometric p-values
    p_values = hypergeom.sf(observed - 1, background, col_sums, row_sums)
    # Compute odds ratios
    with np.errstate(divide="ignore", invalid="ignore"):
        odds_ratios = np.where(
            (observed * (background - row_sums - col_sums + observed)) > 0,
            (observed * (background - row_sums - col_sums + observed))
            / ((row_sums - observed) * (col_sums - observed)),
            np.nan,
        )
    # Apply FDR correction
    fdrs = _apply_fdr_correction(p_values)

    return StatResult(
        p_values=p_values,
        fdrs=fdrs,
        odds_ratios=odds_ratios,
    )


def compute_poisson_test(
    windows: csr_matrix,
    annotations: csr_matrix,
    null_distribution: str = "input",
) -> StatResult:
    """
    Compute Poisson enrichment p-values.

    Args:
        windows (csr_matrix): Binary matrix of windows x labels.
        annotations (csr_matrix): Binary matrix of terms x labels.
        null_distribution (str): 'input' or 'annotations'.

    Returns:
        StatResult: Enrichment p-value matrices.

    Raises:
        ValueError: If null_distribution is not 'input' or 'annotations'.
    """
    overlap = (windows @ annotations.T).toarray()

    if null_distribution == "input":
        lambdas = np.mean(overlap, axis=1, keepdims=True)
    elif null_distribution == "annotations":
        lambdas = np.mean(overlap, axis=0, keepdims=True)
    else:
        raise ValueError("null_distribution must be 'input' or 'annotations'")

    # Compute Poisson p-values
    p_values = 1 - poisson.cdf(overlap - 1, lambdas)
    # Compute odds ratios
    odds_ratios = np.full_like(overlap, np.nan, dtype=float)
    # Apply FDR correction
    fdrs = _apply_fdr_correction(p_values)

    return StatResult(
        p_values=p_values,
        fdrs=fdrs,
        odds_ratios=odds_ratios,
    )


def _apply_fdr_correction(p_values: np.ndarray) -> np.ndarray:
    """
    Safely apply FDR correction to p-values.

    Args:
        p_values (np.ndarray): P-values.

    Returns:
        np.ndarray: FDR-corrected p-values.
    """
    # Check if p_values are empty
    if p_values.size == 0:
        return np.zeros_like(p_values)
    # Check if p_values are 1D arrays
    fdrs = multipletests(p_values.flatten(), method="fdr_bh")[1].reshape(p_values.shape)
    return fdrs
