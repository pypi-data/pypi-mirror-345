"""
slide/input/formats/load_networkx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Optional

import networkx as nx

from slide.input.base import Input2D
from slide.input.formats._loader import load_matrix
from slide.input.formats._log_loading import log_pairs


class LoadNetworkX:
    """Load NetworkX files into Input objects."""

    def load_networkx(
        self, G: nx.Graph, source_axis: str = "row", fill_value: Optional[float] = None
    ) -> Input2D:
        """
        Load a NetworkX graph into a Input object.

        Args:
            G (nx.Graph): A NetworkX graph.
            source_axis (str, optional): Axis to use for the source. Defaults to "row".
            fill_value (Optional[float]): Value to fill NaNs in the matrix. Defaults to None.

        Returns:
            Input2D: A 2D Input object.

        Raises:
            ValueError: If the graph cannot be converted to a DataFrame.
            ValueError: If the source_axis is not 'row' or 'col'.
        """
        log_pairs(filetype="NetworkX")
        try:
            df = nx.to_pandas_adjacency(G)
        except Exception as e:
            raise ValueError(f"Error converting networkx graph to adjacency matrix: {e}")

        return load_matrix(df, source_axis=source_axis, fill_value=fill_value)
