"""
slide/input/io
~~~~~~~~~~~~~~
"""

from slide.input.formats import (
    LoadArray,
    LoadCSV,
    LoadCytoscape,
    LoadDataFrame,
    LoadDict,
    LoadExcel,
    LoadGPickle,
    LoadJSON,
    LoadNetworkX,
    LoadTSV,
)


class InputIO(
    LoadArray,
    LoadCSV,
    LoadCytoscape,
    LoadDataFrame,
    LoadDict,
    LoadExcel,
    LoadGPickle,
    LoadJSON,
    LoadNetworkX,
    LoadTSV,
):
    """
    A class for loading various input formats into SLIDE Input objects.

    This class handles the validation and conversion of various input formats into a unified Input
    object. Supported input formats include TSV, CSV, Excel, JSON, Cytoscape files, gpickle, NetworkX graphs,
    NumPy arrays, DataFrames, and dictionaries.
    """

    def __init__(self):
        super().__init__()
