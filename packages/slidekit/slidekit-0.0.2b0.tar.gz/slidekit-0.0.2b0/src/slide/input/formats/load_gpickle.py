"""
slide/input/formats/load_gpickle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Optional

import networkx as nx
import pandas as pd

from slide.input.base import Input2D
from slide.input.formats._loader import load_matrix
from slide.input.formats._log_loading import log_network


class LoadGPickle:
    """Load GPickle files into Input objects."""

    def load_gpickle(
        self, filepath: str, source_axis: str = "row", fill_value: Optional[float] = None
    ) -> Input2D:
        """
        Convert the contents of a GPickle file to a Input.

        Args:
            filepath (str): Path to the GPickle file.
            source_axis (str, optional): Axis to use for the source. Defaults to "row".
            fill_value (Optional[float]): Value to fill NaNs in the matrix. Defaults to None.

        Returns:
            Input2D: A 2D Input object.

        Raises:
            IOError: If file can't be read.
            ValueError: If the source_axis is not 'row' or 'col'.
        """
        log_network(filetype="GPickle", filepath=filepath)
        try:
            obj = pd.read_pickle(filepath)
            if isinstance(obj, nx.Graph):
                df = nx.to_pandas_adjacency(obj)
            else:
                df = obj
        except Exception as e:
            raise IOError(f"Error reading gpickle file {filepath}: {e}")

        return load_matrix(df, source_axis=source_axis, fill_value=fill_value)
