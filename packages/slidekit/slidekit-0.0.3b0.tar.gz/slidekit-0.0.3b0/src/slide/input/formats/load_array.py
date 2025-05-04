"""
slide/input/formats/load_array
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Any, Optional

import numpy as np
import pandas as pd

from slide.input.base import Input1D, Input2D
from slide.input.formats._loader import (
    DEFAULT_SOURCE_COL,
    DEFAULT_TARGET_COL,
    DEFAULT_VALUE_COL,
    load_matrix,
    load_pairs,
    load_ranked,
)
from slide.input.formats._log_loading import log_matrix, log_pairs, log_ranked


class LoadArray:
    """
    Unified loader for array-like inputs into Input objects.

    This class supports both 1D and 2D data provided as NumPy arrays, lists, tuples,
    or (for 1D) sets. It converts the input to a NumPy array, then to a pandas DataFrame,
    and finally standardizes the DataFrame into a Input via helper functions.
    """

    def _to_numpy(self, arr: Any) -> np.ndarray:
        """
        Convert an array-like structure (list, tuple, etc.) to a NumPy array.

        Args:
            arr (Any): The array-like input.

        Returns:
            np.ndarray: The input converted to a NumPy array.

        Raises:
            ValueError: If the input cannot be converted.
        """
        try:
            return np.array(arr)
        except Exception as e:
            raise ValueError(f"Input cannot be converted to a NumPy array: {e}")

    def load_input_ranked_array(self, arr: Any, fill_value: Optional[float] = None) -> Input1D:
        """
        Load a 1D array-like structure as a ranked list. Accepts 1D arrays or 2D arrays with
        two columns. The first column is treated as the target, and the second column is treated
        as the rank value.
        The second column is optional and can be used to specify edge weights or values.

        Args:
            arr (Any): A 1D array-like input (np.ndarray, list, or tuple).
            fill_value (Optional[float]): Value to fill NaNs. Defaults to None.

        Returns:
            Input1D: A 1D Input.

        Raises:
            ValueError: If the input is not a 1D array-like structure or conversion fails.
        """
        log_ranked(filetype="Array")
        # Convert 1D array to DataFrame
        np_arr = arr if isinstance(arr, np.ndarray) else self._to_numpy(arr)
        if np_arr.ndim == 2 and np_arr.shape[1] == 2:
            df = pd.DataFrame(np_arr, columns=[DEFAULT_TARGET_COL, DEFAULT_VALUE_COL])
        elif np_arr.ndim == 1:
            df = pd.DataFrame({DEFAULT_TARGET_COL: np_arr, DEFAULT_VALUE_COL: range(len(np_arr))})
        else:
            raise ValueError(
                f"Expected 1D array or 2D array with shape (n, 2). Got shape: {np_arr.shape}"
            )

        return load_ranked(
            df, target_col=DEFAULT_TARGET_COL, value_col=DEFAULT_VALUE_COL, fill_value=fill_value
        )

    def load_input_pairs_array(
        self,
        arr: Any,
        fill_value: Optional[float] = None,
    ) -> Input2D:
        """
        Load a paired edge list from a 2D array-like structure. Accepts 2D arrays with
        two or three columns. The first column is treated as the source, the second column
        as the target, and the optional third column as the rank value.
        The third column is optional and can be used to specify edge weights or values.

        Args:
            arr (Any): A 2D array-like input with shape (n, 2) or (n, 3) representing
                [source, target, (value)].
            fill_value (Optional[float]): Value to fill NaNs. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            ValueError: If the input is not a valid 2D edge array-like structure.
        """
        log_pairs(filetype="Array")
        # Convert 2D array to DataFrame
        np_arr = arr if isinstance(arr, np.ndarray) else self._to_numpy(arr)
        try:
            if np_arr.shape[1] == 2:
                # For 2-column arrays, create the DataFrame and add a value column
                df = pd.DataFrame(np_arr, columns=[DEFAULT_SOURCE_COL, DEFAULT_TARGET_COL])
                df[DEFAULT_VALUE_COL] = fill_value
            elif np_arr.shape[1] == 3:
                # For 3-column arrays, use the provided or default value column name
                df = pd.DataFrame(
                    np_arr, columns=[DEFAULT_SOURCE_COL, DEFAULT_TARGET_COL, DEFAULT_VALUE_COL]
                )
            else:
                raise ValueError(
                    f"Input must be a 2D array-like structure with 2 or 3 columns. Current shape: {np_arr.shape}"
                )
        except Exception as e:
            raise ValueError(f"Error converting edge array to DataFrame: {e}")

        return load_pairs(
            df,
            source_col=DEFAULT_SOURCE_COL,
            target_col=DEFAULT_TARGET_COL,
            value_col=DEFAULT_VALUE_COL,
            fill_value=fill_value,
        )

    def load_input_matrix_array(
        self, arr: Any, source_axis: str = "row", fill_value: Optional[float] = None
    ) -> Input2D:
        """
        Load a 2D array-like structure as an adjacency matrix. The first row and column are treated
        as the source and target labels, respectively. The remaining values are treated as the rank
        values.


        Args:
            arr (Any): A 2D array-like input (np.ndarray, list-of-lists, or tuple-of-tuples).
            source_axis (str, optional): Axis for source labels. Use 'row' for row-based sources
                and 'col' for column-based sources. Defaults to 'row'.
            fill_value (Optional[float]): Value to fill NaNs. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            ValueError: If the input is not a valid 2D adjacency matrix.
            ValueError: If the source_axis is not 'row' or 'col'.
        """
        log_matrix(filetype="Array")
        # Check if input is a 2D array-like structure
        np_arr = arr if isinstance(arr, np.ndarray) else self._to_numpy(arr)
        if np_arr.ndim != 2:
            raise ValueError(
                f"Input must be a 2D array-like structure. Current shape: {np_arr.shape}"
            )

        # Convert 2D array to DataFrame
        try:
            df = pd.DataFrame(np_arr)
        except Exception as e:
            raise ValueError(f"Error converting 2D array to DataFrame: {e}")

        return load_matrix(df, source_axis=source_axis, fill_value=fill_value)
