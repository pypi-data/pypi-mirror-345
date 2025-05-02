"""
slide/annotations/base
~~~~~~~~~~~~~~~~~~~~~~
"""

import copy
import statistics
from typing import Any, Dict, List, Optional

from scipy.sparse import csr_matrix, lil_matrix

from slide.log import log_describe


class Annotations:
    """
    Container for SLIDE annotations data.

    This class encapsulates SLIDE annotation data and provides a standardized interface
    for accessing and summarizing the annotations.
    """

    def __init__(self, data: Dict[str, List], min_labels_per_term: int = 0) -> None:
        """Initialize a new Annotations instance.

        Args:
            data (Dict[str, List]): The annotation data where keys are annotation terms and
                values are lists of label IDs.
            min_labels_per_term (Optional[int]): If provided, filter out annotation terms with fewer than
                this number of labels. If filtering results in no terms, a ValueError is raised.
                Defaults to 0.

        Raises:
            ValueError: If no annotation terms remain after filtering.
        """
        self.data = data
        self._metadata = {}
        # Filter the annotations once at instantiation
        self._filtered_data = self._clean_and_filter_annotations(
            self.data, min_labels_per_term or 0
        )

    def to_dict(self) -> Dict[str, List]:
        """
        Return a deep copy of the filtered annotations data.

        Returns:
            Dict[str, List]: A deep copy of the filtered annotations dictionary.
        """
        return copy.deepcopy(self._filtered_data)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return a copy of the metadata.

        Returns:
            Dict[str, Any]: A copy of the metadata dictionary.
        """
        return self._metadata.copy()

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set or update a metadata entry.

        Args:
            key (str): The metadata key.
            value (Any): The metadata value.
        """
        self._metadata[key] = value

    def summary(self) -> Dict[str, Any]:
        """
        Return a summary of the annotations.

        Returns:
            Dict[str, Any]: A summary of the annotations including various statistics.
        """
        # Calculate summary statistics
        counts = [len(labels) for labels in self._filtered_data.values()]
        total_labels = sum(counts)
        num_terms = len(self._filtered_data)
        min_labels = min(counts) if counts else 0
        max_labels = max(counts) if counts else 0
        median_labels = statistics.median(counts) if counts else 0
        mean_labels = statistics.mean(counts) if counts else 0
        unique_labels = {label for labels in self._filtered_data.values() for label in labels}
        return {
            "num_terms": num_terms,
            "total_labels": total_labels,
            "min_labels_per_term": min_labels,
            "max_labels_per_term": max_labels,
            "median_labels_per_term": median_labels,
            "mean_labels_per_term": mean_labels,
            "num_unique_labels": len(unique_labels),
        }

    def describe(self) -> None:
        """
        Print a detailed summary of the Annotations, integrating both summary statistics
        and metadata information.
        """
        log_describe("Annotations Summary", self.summary(), key_width=30, log_level="warning")

    def to_csr(self, label_universe: Optional[List[str]] = None) -> csr_matrix:
        """
        Convert the filtered annotations data to a CSR matrix. Computes the union of all labels
        in the filtered data and sorts them to define the columns.

        Args:
            label_universe (Optional[List[str]]): If provided, this list is used as the label universe.
                Otherwise, the union of all labels in the filtered data is used. Defaults to None.

        Returns:
            csr_matrix: The annotation matrix in CSR format.
        """
        if label_universe is None:
            label_universe = sorted(
                {label for labels in self._filtered_data.values() for label in labels}
            )

        label_to_index = {label: idx for idx, label in enumerate(label_universe)}
        num_terms = len(self._filtered_data)
        num_labels = len(label_universe)

        # Create a sparse matrix
        mat = lil_matrix((num_terms, num_labels), dtype=int)
        for i, (_, labels) in enumerate(self._filtered_data.items()):
            for label in labels:
                if label in label_to_index:
                    mat[i, label_to_index[label]] = 1

        return csr_matrix(mat)

    def _clean_and_filter_annotations(
        self,
        annotations_input: Dict[str, List],
        min_labels_per_term: int = 2,
    ) -> Dict[str, List]:
        """
        Clean and filter annotations based on the minimum number of labels.

        Args:
            annotations_input (Dict[str, List]): Dictionary mapping annotation terms to a list of labels.
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.

        Returns:
            Dict[str, List]: Cleaned and filtered annotations dictionary.

        Raises:
            ValueError: If no annotation terms remain after filtering
        """
        # Clean the loaded dictionary by converting terms and labels to strings and trimming whitespace
        annotations_cleaned = {
            str(term).strip(): [str(x).strip() for x in items]
            for term, items in annotations_input.items()
        }
        # Filter the annotations based on the minimum number of labels
        annotations_filtered = {
            term: items
            for term, items in annotations_cleaned.items()
            if len(items) >= min_labels_per_term
        }
        if not annotations_filtered:
            raise ValueError("No annotation terms remain after filtering.")

        return annotations_filtered
