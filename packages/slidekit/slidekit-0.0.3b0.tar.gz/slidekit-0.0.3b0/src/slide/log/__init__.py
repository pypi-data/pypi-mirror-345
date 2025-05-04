"""
slide/log
~~~~~~~~~
"""

from slide.log.console import (
    log_describe,
    log_header,
    log_loading,
    logger,
    set_global_verbosity,
)
from slide.log.parameters import Params

# Initialize the global parameters logger
params = Params()
params.initialize()
