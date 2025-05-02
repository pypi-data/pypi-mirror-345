"""
slide/input/formats/_log_loading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from functools import partial

from slide.log import log_loading

# Partial functions for logging loading operations
log_ranked = partial(log_loading, header="Loading Ranked List", log_level="info")
log_pairs = partial(log_loading, header="Loading Paired Edge List", log_level="info")
log_matrix = partial(log_loading, header="Loading Adjacency Matrix", log_level="info")
log_network = partial(log_loading, header="Loading Network", log_level="info")
