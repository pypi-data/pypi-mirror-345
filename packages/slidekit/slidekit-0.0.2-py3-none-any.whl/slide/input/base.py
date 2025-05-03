"""
slide/input/base
~~~~~~~~~~~~~~~~
"""

import abc
from typing import Any, Callable, Dict, List, Optional, TypeVar

import pandas as pd

from slide.log import log_describe

# Type variable for SLIDE Input subclasses
T = TypeVar("T", bound="Input")


class Input:
    """Base class for SLIDE Input containers."""

    def __init__(self, data: pd.DataFrame, target_col: str, value_col: str):
        """
        Initialize a new Input1D.

        Args:
            data (pd.DataFrame): The input data.
            target_col (str): Column name for the target labels.
            value_col (str): Column name for the values.
        """
        self.data = data
        self.target_col = target_col
        self.value_col = value_col
        self._metadata = {}
        self._original_data = data.copy()  # Keep a copy of the original data

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get the metadata dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing metadata.
        """
        return self._metadata.copy()

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set a metadata key-value pair.

        Args:
            key (str): The metadata key.
            value (Any): The metadata value.
        """
        self._metadata[key] = value

    @abc.abstractmethod
    def validate(self) -> None:
        """Validate the Input data."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_targets(self) -> List[str]:
        """Get the target labels for the active anchor label."""
        raise NotImplementedError

    @abc.abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Return a summary of the Input."""
        raise NotImplementedError

    def rank(self: T, sort_by: Optional[Callable] = None, ascending: bool = False) -> T:
        """
        Rank the data based on the specified column.

        Args:
            sort_by (Optional[Callable]): A callable to sort the data. If None, uses the default sort.
            ascending (bool): If True, sort in ascending order. Defaults to False.

        Returns:
            T: The ranked Input instance.

        Raises:
            ValueError: If sort_by is not a callable or None.
        """
        if sort_by is None:
            self._active_1d_data = self._active_1d_data.reindex(
                self._active_1d_data[self.value_col].sort_values(ascending=ascending).index
            )
        elif callable(sort_by):
            self._active_1d_data = self._active_1d_data.sort_values(
                by=self.value_col, key=sort_by, ascending=ascending
            )
        else:
            raise ValueError("sort_by must be a callable or None.")

        # Store metadata about the sorting operation
        self.set_metadata("sort_by", sort_by or "sort_values")  # Panda's default
        self.set_metadata("sort_by_ascending", ascending)

        return self

    def describe(self) -> None:
        """
        Print a detailed summary of the Input instance, including all expected summary attributes.
        Missing attributes are displayed as None, indicating incomplete class state.
        """
        # Define expected keys for summary and metadata
        expected_keys = [
            "converted_from",
            "source_col",
            "target_col",
            "value_col",
            "anchor",
            "sort_by",
            "sort_by_ascending",
            "type",
            "shape",
            "num_sources",
            "num_targets",
            "num_pairs",
        ]
        summary = self.summary()
        metadata = self.get_metadata()

        # Combine expected keys with metadata and summary
        combined = {}
        for key in expected_keys:
            combined[key] = summary.get(key, metadata.get(key, None))
        # Include any remaining metadata/summary keys not in expected_keys
        for d in (summary, metadata):
            for key, value in d.items():
                if key not in combined:
                    combined[key] = value

        log_describe(
            f"{self.__class__.__name__} Summary", combined, key_width=30, log_level="warning"
        )


class Input1D(Input):
    """Container for a ranked list in 1D format, with optional metadata tracking."""

    def __init__(self, data: pd.DataFrame, target_col: str, value_col: str):
        """
        Initialize a new Input1D.

        Args:
            data (pd.DataFrame): The input data.
            target_col (str): Column name for the target labels.
            value_col (str): Column name for the values.
        """
        # For 1D, active data is the same as data
        self._active_1d_data = data
        super().__init__(data, target_col, value_col)

    def validate(self) -> None:
        """
        Validate the Input1D data.

        Raises:
            ValueError: If the data contains NaN values or if required columns are missing.
        """
        if self.data.isnull().values.any():
            raise ValueError(
                "Input1D contains NaN values. Clean your data with df.dropna() or df.fillna(0)."
            )
        if self.target_col not in self.data.columns:
            raise ValueError("Input1D must contain a target column.")
        if self.value_col not in self.data.columns:
            raise ValueError("Input1D must contain a value column.")

    def get_targets(self, data: bool = False) -> List[Any]:
        """
        Get the ranked target labels, optionally with associated values.

        Args:
            data (bool): If True, return list of (label, value) tuples. Otherwise, return labels only.

        Returns:
            List: List of labels or list of (label, value) pairs.

        Raises:
            RuntimeError: If no data is available to retrieve targets from.
        """
        if self._active_1d_data.empty:
            raise RuntimeError("No data available to retrieve targets from.")

        if not data:
            return self._active_1d_data[self.target_col].tolist()

        return list(
            zip(
                self._active_1d_data[self.target_col],
                self._active_1d_data[self.value_col],
            )
        )

    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of the Input1D.

        Returns:
            Dict[str, Any]: A dictionary with summary information.
        """
        summ = self.get_metadata()
        summ.update(
            {
                "type": "1d",
                "shape": self.data.shape,
                "num_items": self.data.shape[0],
            }
        )
        return summ


class Input2D(Input):
    """
    Container for a ranked list in 2D paired edge list format, with optional metadata tracking.
    Provides an additional method `select` to choose an anchor label.
    """

    def __init__(self, data: pd.DataFrame, source_col: str, target_col: str, value_col: str):
        """
        Initialize a new Input2D.

        Args:
            data (pd.DataFrame): The input data.
            source_col (str): Column name for the source labels.
            target_col (str): Column name for the target labels.
            value_col (str): Column name for the edge values.
        """
        # Unique to 2D: source column
        self.source_col = source_col
        # For 2D, the active 1D view is initially empty until an anchor is selected
        self._active_1d_data = pd.DataFrame()
        super().__init__(data, target_col, value_col)

    def validate(self) -> None:
        """
        Validate the Input2D data.

        Raises:
            ValueError: If the data contains NaN values or if required columns are missing.
        """
        if self.data.isnull().values.any():
            raise ValueError(
                "Input2D contains NaN values. Clean your data with df.dropna() or df.fillna(0)."
            )
        if self.source_col not in self.data.columns:
            raise ValueError("Input2D must contain a source column.")
        if self.target_col not in self.data.columns:
            raise ValueError("Input2D must contain a target column.")
        if self.value_col not in self.data.columns:
            raise ValueError("Input2D must contain a value column.")

    def select(self, anchor: str) -> "Input2D":
        """
        Select an anchor label to filter the data for a 1D view.

        Args:
            anchor (str): The anchor label to select.

        Returns:
            Input2D: A new Input2D with the active anchor label.

        Raises:
            ValueError: If the anchor label is not found in the source column.
        """
        # Check if anchor exists in the source column
        unique_sources = self.data[self.source_col].unique().tolist()
        if anchor not in unique_sources:
            available = ", ".join(unique_sources[:5])
            more = ", ..." if len(unique_sources) > 5 else ""
            raise ValueError(f"Anchor '{anchor}' not found. Available anchors: {available}{more}")

        # Filter data for the selected anchor
        filtered = self.data[self.data[self.source_col] == anchor].copy()
        self._active_1d_data = filtered[[self.target_col, self.value_col]]
        self.set_metadata("anchor", anchor)

        return self

    def get_targets(self, data: bool = False) -> List[Any]:
        """
        Get the target labels for the active anchor label, optionally with associated values.

        Args:
            data (bool): If True, return list of (label, value) tuples. Otherwise, return labels only.

        Returns:
            List: List of labels or list of (label, value) pairs.

        Raises:
            RuntimeError: If no anchor is selected.
        """
        if self._active_1d_data.empty:
            raise RuntimeError("No anchor selected. Use .select(anchor) before getting targets.")

        if not data:
            return self._active_1d_data[self.target_col].tolist()

        return list(
            zip(
                self._active_1d_data[self.target_col],
                self._active_1d_data[self.value_col],
            )
        )

    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of the Input2D.

        Returns:
            Dict[str, Any]: A dictionary with summary information.
        """
        summ = self.get_metadata()
        summ.update(
            {
                "type": "2d",
                "shape": self.data.shape,
                "num_sources": self.data[self.source_col].nunique(),
                "num_targets": self.data[self.target_col].nunique(),
                "num_pairs": self.data.shape[0],
            }
        )
        return summ
