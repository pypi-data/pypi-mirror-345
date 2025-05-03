"""
slide/analysis/loader
~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Set, Tuple, Union

import numpy as np

from slide.analysis.base import Analysis
from slide.annotation.base import Annotation
from slide.input.base import Input1D, Input2D


class AnalysisLoader:
    """
    Public-facing analysis loader class for integration with the SLIDE framework.

    This class provides a public constructor for creating an Analysis object,
    which ties together a sorted list of gene labels with annotation terms,
    applies a sliding window, and computes enrichment statistics.
    """

    def load_analysis(
        self,
        input_container: Union[Input1D, Input2D],
        annotation: Annotation,
        window_size: Union[int, List[int], Tuple[int], Set[int], np.ndarray] = 20,
    ) -> Analysis:
        """
        Public constructor for an Analysis object.

        Args:
            input_container (Input1D or Input2D): Preprocessed input container with sorted labels.
            annotation (Annotation): Annotation object containing term-label mappings.
            window_size (int or iterable of ints): Size(s) of sliding windows to apply.
                Defaults to 20. Can be a single integer or a collection of integers.

        Returns:
            Analysis: An Analysis object ready for enrichment analysis.

        Raises:
            ValueError: If window_size is not a positive int or a collection of positive ints.
        """
        return Analysis(
            input_container=input_container, annotation=annotation, window_size=window_size
        )
