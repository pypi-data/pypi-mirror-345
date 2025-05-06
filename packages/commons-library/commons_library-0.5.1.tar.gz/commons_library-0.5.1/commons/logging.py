import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union
from logging import Logger, DEBUG, INFO, WARNING, WARN, ERROR

Level = Union[DEBUG, INFO, WARNING, WARN, ERROR]

def config(
        level: int | Level = INFO,
        format: str = '%(asctime)s.%(msecs)03d - %(name)s [%(levelname)s]: %(message)s',
        datefmt: Optional[str] = "%Y-%m-%d %H:%M:%S",  # ISO 8601 format,
        directory: Optional[Union[Path, str]] = None,
        max_file_bytes: int = 1024 * 1024,  # 1 MB
        backup_count: int = 5,
        stream=sys.stdout,
) -> Logger:
    """
    Configure global logging settings, including file logging if a directory is provided.

    :param level: The logging level (e.g., logging.INFO, logging.DEBUG).
    :param format: The logging format string.
    :param datefmt: The date/time format string.
    :param app_name: The name of the application. Used for naming the log file.
    :param directory: The directory where log files will be stored.
    :param max_file_bytes: The maximum size of a log file before it is rotated.
    :param backup_count: The number of backup log files to keep.
    :param stream: A stream to use for logging (e.g., sys.stdout, sys.stderr).
    """
    # Get the root logger
    logger = logging.getLogger()

    # Configure handlers for the root logger
    # Remove existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Create a formatter
    formatter = logging.Formatter(format, datefmt)

    # Add a console handler if a stream is not provided
    if stream is not None:
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Add a file handler if a directory is provided
    if directory:
        directory = Path(directory)
        if not directory.exists():
            directory.mkdir(exist_ok=True, parents=True)
        log_file = directory / f"{logger.name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_bytes,
            backupCount=backup_count,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(level)

    return logger


def get_logger(
        name: Optional[str | type] = None,
        level: Optional[int | Level] = None,
        propagate: bool = True
) -> Logger:
    """
    Get a logger with the specified name. Inherits configurations from the global logger by default,
    but can be configured with distinct settings.

    :param name: The name of the logger.
    :param level: The logging level. If None, inherits from the global logger.
    :param propagate: Whether to propagate messages to parent loggers.
    :return: The configured logger instance.
    """
    from inspect import getmodule

    if name is None:
        logger = logging.getLogger()  # get root logger
    else:
        if isinstance(name, type):
            name = f"{getmodule(name).__name__}.{name.__name__}"
        else:
            name = str(name)
        logger = logging.getLogger(name)

    # Set the logging level if provided
    if level is not None:
        logger.setLevel(level)

    # Configure propagation
    logger.propagate = propagate

    return logger
