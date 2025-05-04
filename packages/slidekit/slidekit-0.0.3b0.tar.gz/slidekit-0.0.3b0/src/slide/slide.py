"""
slide/slide
~~~~~~~~~~~
"""

from slide.analysis.loader import AnalysisLoader
from slide.annotation.io import AnnotationIO
from slide.input.io import InputIO
from slide.log import params, set_global_verbosity


class SLIDE(InputIO, AnnotationIO, AnalysisLoader):
    """
    SLIDE: A class for ranked list analysis and annotation support.

    The SLIDE class provides tools for loading and transforming ranked feature lists,
    validating data formats, integrating external annotation, and enabling downstream
    functional analysis or visualization based on ranked relationships.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the SLIDE class with configuration settings.

        Args:
            verbose (bool): If False, suppresses all log messages to the console. Defaults to True.
        """
        # Set global verbosity for logging
        set_global_verbosity(verbose)
        # Provide public access to network parameters
        self.params = params
        super().__init__()
