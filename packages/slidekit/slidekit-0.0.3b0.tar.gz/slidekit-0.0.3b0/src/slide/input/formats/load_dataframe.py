"""
slide/input/formats/load_dataframe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


class LoadDataFrame:
    """Load DataFrames into Input objects."""

    def load_input_ranked_dataframe(
        self,
        df: pd.DataFrame,
        target_col: str,
        value_col: Optional[str] = None,
        fill_value: Optional[float] = None,
    ) -> Input1D:
        """
        Load a DataFrame representing a 1D ranked list. The first column is treated as the target,
        and the second column is treated as the rank value. The second column is optional and can
        be used to specify edge weights or values.


        Args:
            df (pd.DataFrame): A DataFrame with target and optional value columns.
            target_col (str): Column to use for the target.
            value_col (Optional[str]): Column to use for ranking. Defaults to None.
            fill_value (Optional[float]): Value to fill NaNs in the value column. Defaults to None.

        Returns:
            Input1D: A 1D Input.

        Raises:
            ValueError: If the value column is specified but not found in the DataFrame.
        """
        log_ranked(filetype="DataFrame")
        return load_ranked(df, target_col=target_col, value_col=value_col, fill_value=fill_value)

    def load_input_pairs_dataframe(
        self,
        df: pd.DataFrame,
        source_col: str,
        target_col: str,
        value_col: Optional[str] = None,
        fill_value: Optional[float] = None,
    ) -> Input2D:
        """
        Load a DataFrame representing a paired edge list. The first column is treated as the source,
        and the second column is treated as the target. The third column is treated as the rank value.
        The third column is optional and can be used to specify edge weights or values.

        Args:
            df (pd.DataFrame): A DataFrame with source, target, and optional value columns.
            source_col (str): Name of the source column.
            target_col (str): Name of the target column.
            value_col (Optional[str]): Name of the value/weight column. Defaults to None.
            fill_value (Optional[float]): Value to fill NaNs in the value column. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            ValueError: If the value column is specified but not found in the DataFrame.
        """
        log_pairs(filetype="DataFrame")
        return load_pairs(
            df,
            source_col=source_col,
            target_col=target_col,
            value_col=value_col,
            fill_value=fill_value,
        )

    def load_input_matrix_dataframe(
        self, df: pd.DataFrame, source_axis: str = "row", fill_value: Optional[float] = None
    ) -> Input2D:
        """
        Load a DataFrame representing an adjacency matrix. The first row and column are treated
        as the source and target labels, respectively. The remaining values are treated as the rank
        values.

        Args:
            df (pd.DataFrame): A DataFrame representing an adjacency matrix.
            source_axis (str, optional): Whether to use rows or columns as sources. Defaults to "row".
            fill_value (Optional[float]): Value to fill NaNs in the matrix. Defaults to None.

        Returns:
            Input2D: A 2D Input.

        Raises:
            ValueError: If the DataFrame is not a valid adjacency matrix.
        """
        log_matrix(filetype="DataFrame")
        return load_matrix(df, source_axis=source_axis, fill_value=fill_value)
