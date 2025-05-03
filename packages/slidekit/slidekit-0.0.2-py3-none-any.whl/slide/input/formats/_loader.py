"""
slide/input/formats/_loader
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Optional

import pandas as pd

from slide.input.base import Input1D, Input2D

# Default column names for edge lists
DEFAULT_SOURCE_COL = "source"
DEFAULT_TARGET_COL = "target"
DEFAULT_VALUE_COL = "value"


def load_ranked(
    df: pd.DataFrame,
    target_col: str,
    value_col: Optional[str] = None,
    fill_value: Optional[float] = None,
) -> Input1D:
    """
    Standardize and load a DataFrame as a 1D ranked list.

    Args:
        df (pd.DataFrame): The input DataFrame.
        target_col (str): Column name for the target.
        value_col (Optional[str]): Column name to use for value ranking. Defaults to None.
        fill_value (Optional[float]): Value to fill NaN values in the value column. Defaults to None.

    Returns:
        Input1D: A 1D Input.

    Raises:
        ValueError: If the value column is specified but not found in the DataFrame.
        KeyError: If the target column is missing.
    """
    if value_col and value_col not in df.columns:
        raise ValueError(f"Ranked column '{value_col}' not found in DataFrame.")

    try:
        df[target_col] = df[target_col].astype(str)
    except KeyError:
        raise KeyError(
            f"Target column '{target_col}' not found in DataFrame. Available columns: {list(df.columns)}"
        ) from KeyError

    # Fill NaN values
    if fill_value is not None and value_col in df.columns:
        df[value_col] = df[value_col].fillna(fill_value)
    if value_col is None:
        value_col = "value"
        df[value_col] = 1.0

    # Create Input1D
    sl = Input1D(data=df, target_col=target_col, value_col=value_col)
    sl.validate()
    sl.set_metadata("value_col", value_col)

    return sl


def load_pairs(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    value_col: Optional[str] = None,
    fill_value: Optional[float] = None,
) -> Input2D:
    """
    Standardize and load a DataFrame as a 2D paired edge list.

    Args:
        df (pd.DataFrame): The input DataFrame.
        source_col (str): Column name for the source.
        target_col (str): Column name for the target.
        value_col (Optional[str]): Column name for the value. Defaults to None.
        fill_value (Optional[float]): Value to fill NaN values in the value column. Defaults to None.

    Returns:
        Input2D: A 2D Input.

    Raises:
        ValueError: If the source or target columns are missing or the value column is specified but not found.
        KeyError: If the source or target columns are missing.
    """
    if value_col and value_col not in df.columns:
        raise ValueError(f"Value column '{value_col}' not found in DataFrame.")

    try:
        df[source_col] = df[source_col].astype(str)
        df[target_col] = df[target_col].astype(str)
    except KeyError:
        raise KeyError(
            f"Source or target column not found in DataFrame. Available columns: {list(df.columns)}"
        ) from KeyError

    # Fill NaN values
    if fill_value is not None and value_col in df.columns:
        df[value_col] = df[value_col].fillna(fill_value)
    if value_col is None:
        value_col = "value"
        df[value_col] = 1.0

    # Create Input2D
    sl = Input2D(data=df, source_col=source_col, target_col=target_col, value_col=value_col)
    sl.validate()
    sl.set_metadata("converted_from", "pairs")
    sl.set_metadata("source_col", source_col)
    sl.set_metadata("target_col", target_col)
    sl.set_metadata("value_col", value_col)

    return sl


def load_matrix(
    df: pd.DataFrame, source_axis: str = "row", fill_value: Optional[float] = None
) -> Input2D:
    """
    Standardize and load a DataFrame as a 2D adjacency matrix.

    Args:
        df (pd.DataFrame): The input DataFrame.
        source_axis (str, optional): Axis for source labels. Use 'row' for row-based sources and 'col' for
            column-based sources. Defaults to 'row'.
        fill_value (Optional[float]): Value to fill NaN values in the matrix. Defaults to None.

    Returns:
        Input2D: A 2D Input.

    Raises:
        ValueError: If the source_axis is not 'row' or 'col'.
    """
    df = df.copy()
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(str)

    # Convert to long format
    if source_axis == "row":
        if DEFAULT_SOURCE_COL not in df.columns:
            df.index.name = DEFAULT_SOURCE_COL
            df = df.reset_index()
        df_long = df.melt(
            id_vars=DEFAULT_SOURCE_COL, var_name=DEFAULT_TARGET_COL, value_name=DEFAULT_VALUE_COL
        )
    elif source_axis == "col":
        df = df.transpose()
        if DEFAULT_SOURCE_COL not in df.columns:
            df.index.name = DEFAULT_SOURCE_COL
            df = df.reset_index()
        df_long = df.melt(
            id_vars=DEFAULT_SOURCE_COL, var_name=DEFAULT_TARGET_COL, value_name=DEFAULT_VALUE_COL
        )
    else:
        raise ValueError("Invalid source_axis: must be 'row' or 'col'")

    if fill_value is not None:
        df_long[DEFAULT_VALUE_COL] = df_long[DEFAULT_VALUE_COL].fillna(fill_value)

    # Create Input2D
    sl = Input2D(
        data=df_long,
        source_col=DEFAULT_SOURCE_COL,
        target_col=DEFAULT_TARGET_COL,
        value_col=DEFAULT_VALUE_COL,
    )
    sl.validate()
    sl.set_metadata("source_col", DEFAULT_SOURCE_COL)
    sl.set_metadata("target_col", DEFAULT_TARGET_COL)
    sl.set_metadata("value_col", DEFAULT_VALUE_COL)

    return sl
