"""
slide/input/formats/load_json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Optional

import pandas as pd

from slide.input.base import Input1D, Input2D
from slide.input.formats._loader import (
    load_matrix,
    load_pairs,
    load_ranked,
)
from slide.input.formats._log_loading import log_matrix, log_pairs, log_ranked


class LoadJSON:
    """Load JSON files into Input objects."""

    def load_input_ranked_json(
        self,
        filepath: str,
        target_col: str,
        value_col: Optional[str] = None,
        fill_value: Optional[float] = None,
    ) -> Input1D:
        """
        Load a JSON file representing a 1D ranked list. The first column is treated as the target,
        and the second column is treated as the rank value. The second column is optional and can
        be used to specify edge weights or values.


        Args:
            filepath (str): Path to the JSON file with target and optional value columns.
            target_col (str): Column name for the target.
            value_col (Optional[str]): Column name to use for ranking. Defaults to None.
            fill_value (Optional[float]): Value to fill NaN values in the value column. Defaults to None.

        Returns:
            Input1D: A 1D Input.

        Raises:
            IOError: If the file can not be read.
            ValueError: If the value column is specified but not found in the DataFrame.
        """
        df = self._read_json(filepath=filepath, filetype="ranked")
        return load_ranked(df, target_col=target_col, value_col=value_col, fill_value=fill_value)

    def load_input_pairs_json(
        self,
        filepath: str,
        source_col: str,
        target_col: str,
        value_col: Optional[str] = None,
        fill_value: Optional[float] = None,
    ) -> Input2D:
        """
        Load a JSON file representing a paired edge list. The first column is treated as the source,
        and the second column is treated as the target. The third column is treated as the rank value.
        The third column is optional and can be used to specify edge weights or values.

        Args:
            filepath (str): Path to the JSON file with source, target, and optional value columns.
            source_col (str): Source column name.
            target_col (str): Target column name.
            value_col (Optional[str]): Column name for edge weights. Defaults to None.
            fill_value (Optional[float]): Value to fill NaN values in the value column. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            IOError: If the file can not be read.
            ValueError: If the source_col or target_col is not found in the DataFrame.
        """
        df = self._read_json(filepath=filepath, filetype="pairs")
        return load_pairs(
            df,
            source_col=source_col,
            target_col=target_col,
            value_col=value_col,
            fill_value=fill_value,
        )

    def load_input_matrix_json(
        self, filepath: str, source_axis: str = "row", fill_value: Optional[float] = None
    ) -> Input2D:
        """
        Load a JSON file representing an adjacency matrix. The first key is treated as the source,
        and the second key is treated as the target. The remaining values are treated as the rank
        values. The source_axis parameter determines whether the first key is treated as the row or
        column labels.

        Args:
            filepath (str): Path to the JSON file representing an adjacency matrix.
            source_axis (str, optional): Axis for source labels. Use 'row' for row-based sources and 'col' for
                column-based sources. Defaults to 'row'.
            fill_value (Optional[float]): Value to fill NaN values in the value column. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            IOError: If the file can not be read.
            ValueError: If the source_axis is not 'row' or 'col'.
        """
        df = self._read_json(filepath=filepath, filetype="matrix")
        return load_matrix(df, source_axis=source_axis, fill_value=fill_value)

    def _read_json(self, filepath: str, filetype: str) -> pd.DataFrame:
        """
        Read a JSON file and return a DataFrame.

        Args:
            filepath (str): Path to the JSON file.
            filetype (str): Type of JSON file (ranked, pairs, matrix).

        Returns:
            pd.DataFrame: DataFrame containing the data from the JSON file.

        Raises:
            IOError: If the file can't be read.
        """
        log_func = {
            "ranked": log_ranked,
            "pairs": log_pairs,
            "matrix": log_matrix,
        }.get(filetype)

        if log_func:
            log_func(filetype="JSON", filepath=filepath)

        try:
            return pd.read_json(filepath)
        except Exception as e:
            raise IOError(f"Error reading JSON file {filepath}: {e}")
