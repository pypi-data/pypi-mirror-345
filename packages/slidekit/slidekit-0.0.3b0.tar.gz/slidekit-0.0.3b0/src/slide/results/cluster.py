"""
slide/results/cluster
~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Literal, Union

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.metrics import silhouette_score


def cluster_enrichment_profiles(
    enrichment_df: pd.DataFrame,
    method: str = "average",
    metric: str = "jaccard",
    threshold: Union[str, float] = "auto",
    criterion: Literal["distance", "maxclust"] = "distance",
) -> pd.Series:
    """
    Clusters rows (e.g., terms) in the enrichment matrix based on similarity.

    Args:
        enrichment_df (pd.DataFrame): A binary or continuous matrix (terms x windows), where values
            represent presence or strength of enrichment.
        method (str): Linkage method for hierarchical clustering. Default is 'average'.
        metric (str): Distance metric for pairwise comparisons. Default is 'jaccard'.
        threshold (Union[str, float]): Distance threshold or number of clusters.
            If "auto", threshold is set to 0.5 * max linkage distance.
        criterion (Literal["distance", "maxclust"]): Criterion for cluster assignment.

    Returns:
        pd.Series: A Series mapping index labels in `enrichment_df` to assigned cluster IDs.

    Raises:
        ValueError: If the input DataFrame has fewer than 2 rows or if the threshold is invalid.
    """
    if enrichment_df.shape[0] < 2:
        raise ValueError("Clustering requires at least 2 rows.")

    matrix = enrichment_df.fillna(0).astype(float).to_numpy()
    # Check for non-finite values
    if not np.isfinite(matrix).all():
        raise ValueError(
            "Input matrix contains non-finite values (inf or nan), which are not supported."
        )

    # Compute the condensed distance matrix
    condensed_dist = pdist(matrix, metric=metric)
    Z = linkage(condensed_dist, method=method)
    # Determine the threshold for clustering
    if isinstance(threshold, str) and threshold == "auto":
        if criterion == "distance":
            threshold_value = _auto_silhouette_threshold(Z, matrix, metric)
        else:
            raise ValueError("Auto threshold only supported for 'distance' criterion.")
    elif isinstance(threshold, (int, float)):
        threshold_value = threshold
    else:
        raise ValueError(f"Invalid threshold value: {threshold}")

    # Determine clusters based on the threshold
    cluster_ids = fcluster(Z, t=threshold_value, criterion=criterion)
    cluster_series = pd.Series(cluster_ids, index=enrichment_df.index)

    return cluster_series


def _auto_silhouette_threshold(
    Z: np.ndarray,
    matrix: np.ndarray,
    metric: str,
    frac_range: np.ndarray = np.linspace(0.2, 0.8, 7),
) -> float:
    """
    Find optimal silhouette threshold from a range of fractions of max linkage height.

    Args:
        Z (np.ndarray): Linkage matrix from hierarchical clustering.
        matrix (np.ndarray): Original data matrix.
        metric (str): Distance metric used for clustering.
        frac_range (np.ndarray): Range of fractions to test for thresholding.

    Returns:
        float: Optimal threshold for clustering.
    """
    best_score = -1
    best_threshold = None
    # Iterate over the fraction range
    for frac in frac_range:
        try:
            # Calculate the threshold based on the fraction of max linkage height
            t_val = frac * np.max(Z[:, 2])
            labels = fcluster(Z, t=t_val, criterion="distance")
            if len(np.unique(labels)) < 2:
                continue
            # Calculate silhouette score and check if it's the best
            score = silhouette_score(matrix, labels, metric=metric)
            if score > best_score:
                best_score = score
                best_threshold = t_val
        except Exception:
            continue

    return best_threshold if best_threshold is not None else 0.5 * np.max(Z[:, 2])
