"""
slide/log/console
~~~~~~~~~~~~~~~~~
"""

import logging
import shutil
from typing import Literal, Optional


def in_jupyter():
    """
    Check if the code is running in a Jupyter notebook environment.

    Returns:
        bool: True if running in a Jupyter notebook or QtConsole, False otherwise.
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":  # Jupyter Notebook or QtConsole
            return True
        if shell == "TerminalInteractiveShell":  # Terminal running IPython
            return False

        return False  # Other type (?)
    except NameError:
        return False  # Not in Jupyter


# Define the MockLogger class to replicate logging behavior with print statements in Jupyter
class MockLogger:
    """
    MockLogger: A lightweight logger replacement using print statements in Jupyter.

    The MockLogger class replicates the behavior of a standard logger using print statements
    to display messages. This is primarily used in a Jupyter environment to show outputs
    directly in the notebook. The class supports logging levels such as `info`, `debug`,
    `warning`, and `error`, while the `verbose` attribute controls whether to display non-error messages.
    """

    def __init__(self, verbose: Optional[bool] = True):
        """
        Initialize the MockLogger with verbosity settings.

        Args:
            verbose (Optional[bool]): If True, display all log messages (info, debug, warning).
                If False, only display error messages. Defaults to True.
        """
        self.verbose = verbose

    def info(self, message: str) -> None:
        """
        Display an informational message.

        Args:
            message (str): The informational message to be printed.
        """
        if self.verbose:
            print(message)

    def debug(self, message: str) -> None:
        """
        Display a debug message.

        Args:
            message (str): The debug message to be printed.
        """
        if self.verbose:
            print(message)

    def warning(self, message: str) -> None:
        """
        Display a warning message.

        Args:
            message (str): The warning message to be printed.
        """
        print(message)

    def error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message (str): The error message to be printed.
        """
        print(message)

    def setLevel(self, level: int) -> None:
        """
        Adjust verbosity based on the logging level.

        Args:
            level (int): Logging level to control message display.
                - logging.DEBUG sets verbose to True (show all messages).
                - logging.WARNING sets verbose to False (show only warning, error, and critical messages).
        """
        if level == logging.DEBUG:
            self.verbose = True  # Show all messages
        elif level == logging.WARNING:
            self.verbose = False  # Suppress all except warning, error, and critical messages


# Set up logger based on environment
if not in_jupyter():
    # Set up logger normally for .py files or terminal environments
    logger = logging.getLogger("slide_logger")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
else:
    # If in Jupyter, use the MockLogger
    logger = MockLogger()

# Global log level to function mapping
LOG_FUNCTIONS = {
    "info": logger.info,
    "warning": logger.warning,
    "debug": logger.debug,
    "error": logger.error,
}
DEFAULT_LOG_FUNCTION = logger.warning


def set_global_verbosity(verbose):
    """
    Set the global verbosity level for the logger.

    Args:
        verbose (bool): Whether to display all log messages (True) or only error messages (False).

    Returns:
        None
    """
    if not isinstance(logger, MockLogger):
        # For the regular logger, adjust logging levels
        if verbose:
            logger.setLevel(logging.DEBUG)  # Show all messages
            console_handler.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)  # Show only warning, error, and critical messages
            console_handler.setLevel(logging.WARNING)
    else:
        # For the MockLogger, set verbosity directly
        logger.setLevel(logging.DEBUG if verbose else logging.WARNING)


def log_header(
    input_string: str, log_level: Literal["info", "warning", "debug", "error"] = "info"
) -> None:
    """
    Log the input string as a header with a line of dashes above and below it.

    Example:
        >>> log_header("My Header", log_level="info")
        # ------------------------------
        # My Header
        # ------------------------------

    Args:
        input_string (str): The string to be printed as a header.
        log_level (Literal["warning", "info", "debug", "error"], optional): Logging level
            for the message. Defaults to "info".
    """
    border = "-" * len(input_string)
    # Choose the logging function based on the log level
    log_function = LOG_FUNCTIONS.get(log_level, DEFAULT_LOG_FUNCTION)
    log_function(border)
    log_function(input_string)
    log_function(border)


def log_loading(
    header: str,
    filetype: str,
    filepath: Optional[str] = "",
    log_level: Literal["info", "warning", "debug", "error"] = "info",
) -> None:
    """
    Log the loading process of a file with its type and path.

    Example:
        >>> log_loading("Loading Data", "CSV", "/path/to/file.csv", log_level="info")
        # ------------------------------
        # Loading Data
        # ------------------------------
        # Filetype: CSV
        # Filepath: /path/to/file.csv

    Args:
        header (str): The header to be printed.
        filetype (str): The type of file being loaded.
        filepath (Optional[str]): The path to the file being loaded. Defaults to an empty string.
        log_level (Literal["warning", "info", "debug", "error"], optional): Logging level
            for the message. Defaults to "info".
    """
    # First, log the header
    log_header(header, log_level=log_level)
    # Choose the logging function based on the log level
    log_function = LOG_FUNCTIONS.get(log_level, DEFAULT_LOG_FUNCTION)
    log_function(f"Filetype: {filetype}")
    if filepath:
        log_function(f"Filepath: {filepath}")


def log_describe(
    header: str,
    items: dict,
    key_width: int = 25,
    log_level: Literal["info", "warning", "debug", "error"] = "warning",
) -> None:
    """
    Log a formatted summary block with a header and aligned key-value pairs.

    Example:
        >>> log_describe("Summary", {"Key1": "Value1", "Key2": "Value2"}, key_width=30, log_level="warning")
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Summary
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Key1                : Value1
        # Key2                : Value2

    Args:
        header (str): Title of the summary block.
        items (dict): Dictionary of key-value pairs to display.
        key_width (int, optional): Width of the key column. Defaults to 25.
        log_level (Literal["warning", "info", "debug", "error"], optional): Logging level
            for the message. Defaults to "warning".
    """
    # Adjust the key width to fit the terminal size
    lines = [f"{k:{key_width}s}: {v}" for k, v in items.items()]
    all_lines = [header] + lines
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    line_length = min(max(len(line) for line in all_lines), terminal_width)
    # Choose the logging function based on the log level
    log_function = LOG_FUNCTIONS.get(log_level, DEFAULT_LOG_FUNCTION)
    log_function("~" * line_length)
    log_function(header)
    log_function("~" * line_length)
    for line in lines:
        log_function(line)
