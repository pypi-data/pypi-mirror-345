"""
slide/input/formats/load_dict
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Dict, Optional

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


class LoadDict:
    """Load dictionaries into Input objects."""

    def load_input_ranked_dict(
        self,
        d: Dict,
        fill_value: Optional[float] = None,
    ) -> Input1D:
        """
        Load a dictionary as a 1D ranked list. The first column is treated as the target,
        and the second column is treated as the rank value. The second column is optional and can
        be used to specify edge weights or values.


        Args:
            d (Dict): A dictionary where keys are items and values are rankable values.
            fill_value (Optional[float]): Value to fill NaN values in the value key. Defaults to None.

        Returns:
            Input1D: A 1D Input.

        Raises:
            ValueError: If the input is not a valid ranked dictionary.
        """
        log_ranked(filetype="Dict")
        try:
            df = pd.DataFrame(list(d.items()), columns=[DEFAULT_TARGET_COL, DEFAULT_VALUE_COL])
        except Exception as e:
            raise ValueError(f"Error converting ranked dictionary to DataFrame: {e}")

        return load_ranked(
            df, target_col=DEFAULT_TARGET_COL, value_col=DEFAULT_VALUE_COL, fill_value=fill_value
        )

    def load_input_pairs_dict(
        self,
        d: Dict,
        fill_value: Optional[float] = None,
    ) -> Input2D:
        """
        Load a dictionary as a paired edge list. The first column is treated as the source,
        and the second column is treated as the target. The third column is treated as the rank value.
        The third column is optional and can be used to specify edge weights or values.

        Args:
            d (Dict): A dictionary of dictionaries or Series, like {a: {b: value}}.
            fill_value (Optional[float]): Value to fill NaNs. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            ValueError: If the input is not a valid edge dictionary.
        """
        log_pairs(filetype="Dict")
        try:
            records = [
                {DEFAULT_SOURCE_COL: src, DEFAULT_TARGET_COL: tgt, DEFAULT_VALUE_COL: val}
                for src, targets in d.items()
                for tgt, val in targets.items()
            ]
            df = pd.DataFrame(records)
        except Exception as e:
            raise ValueError(f"Error converting edge dictionary to DataFrame: {e}")

        return load_pairs(
            df,
            source_col=DEFAULT_SOURCE_COL,
            target_col=DEFAULT_TARGET_COL,
            value_col=DEFAULT_VALUE_COL,
            fill_value=fill_value,
        )

    def load_input_matrix_dict(
        self, d: Dict, source_axis: str = "row", fill_value: Optional[float] = None
    ) -> Input2D:
        """
        Load a dictionary representing an adjacency matrix. The first key is treated as the source,
        and the second key is treated as the target. The remaining values are treated as the rank
        values. The source_axis parameter determines whether the first key is treated as the row or
        column labels.

        Args:
            d (Dict): A dictionary of dictionaries or Series in the form of an adjacency matrix (or a nested dictionary).
            source_axis (str, optional): Which axis is used for source labels. Defaults to "row".
            fill_value (Optional[float]): Value to fill NaNs. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            ValueError: If the input is not a valid adjacency matrix.
            ValueError: If the source_axis is not 'row' or 'col'.
        """
        log_matrix(filetype="Dict")
        try:
            df = pd.DataFrame(d)
        except Exception as e:
            raise ValueError(f"Error converting adjacency dictionary to DataFrame: {e}")

        return load_matrix(df, source_axis=source_axis, fill_value=fill_value)
