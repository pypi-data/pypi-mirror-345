"""Logging module for wtftools package."""

import logging
import sys
from types import MappingProxyType

from dailylog_lib.cache import Cache

LABEL = "label"
WARNING = "WARNING"
LOG_LEVELS = MappingProxyType(
    {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        WARNING: logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    },
)


def _label_to_level(level: str) -> int:
    """
    Convert a log label to its corresponding level.

    Parameters
    ----------
    level : str
        Log level label, e.g. "WARNING", "INFO", etc.

    Raises
    ------
    ValueError
        If the log label is a number.

    Returns
    -------
    int
        The corresponding log level, e.g. logging.WARNING, logging.INFO, etc.
    """
    if level.isdigit():
        raise ValueError("Log label cannot be a number.")
    return LOG_LEVELS.get(level.upper(), logging.WARNING)


def log_label(level: str) -> str:
    """Return logger level name.

    Parameters
    ----------
    level : str
        Level number or name

    Returns
    -------
    str
        Level name, Default if not matched, by default "ERROR"
    """
    if level.isdigit():
        i_level = int(level)
        for key, valor in LOG_LEVELS.items():
            if i_level == valor:
                return key
    else:
        u_level = level.upper()
        if u_level in LOG_LEVELS:
            return u_level

    return WARNING


def log_level(level: int | str) -> int:
    """Return logger level name.

    Parameters
    ----------
    level : str
        Level number or name

    Returns
    -------
    int
        Level, default logging.WARNING
    """
    if isinstance(level, str):
        if level.isdigit():
            level = int(level)
        else:
            return _label_to_level(level)

    for key, valor in LOG_LEVELS.items():
        if level == valor:
            return level

    return logging.WARNING


class Logger(Cache):
    """Logging class for dailylog-lib package."""

    _level: int

    def __init__(self, **kwargs: bool | int | str) -> None:
        """
        Initialize the Cache class with provided keyword arguments.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments that can include:
            - cache (str): Cache file path, optional.
            - config (str): Config file path, optional.
            - debug (bool | int): Debug level, defaults to 0.
            - level (str | int): Log level, defaults to "WARNING".
            - test (bool): Test mode flag, defaults to False.
            - verbose (bool | int): Verbosity level, defaults to 0.

        This constructor initializes the cache by loading it from a file or creating
        a new cache if no file exists.
        """
        super().__init__(**kwargs)
        self._level = log_level(kwargs.get("level", WARNING))

    def log(self, message, **kwargs: bool | int | str) -> None:
        """Log a message with specified parameters, handling suppression and caching.

        Parameters
        ----------
        message : str
            The message to log.
        **kwargs : dict
            Additional keyword arguments:
            - caller (str): Caller name, optional.
            - key (str): Unique key for the cache record, optional.
            - label (str): Log level label, defaults to "ERROR".
            - logfn (str): Path to the log file, defaults to the default log.
            - quiet (bool): If True, suppresses terminal output.
            - suppress (int): Number of seconds to suppress repeated messages,
                defaults to CONST_DAY.
        """
        valor = kwargs.get("caller", "")
        if valor:
            message = "{0} - {1}".format(valor, message)
        if "key" in kwargs:
            self.log_message(str(kwargs.pop("key")), message, **kwargs)
        else:
            label = log_label(str(kwargs.get(LABEL, WARNING)))
            log_fn = str(kwargs.get("logfn", ""))
            if log_fn:
                Cache.append_daily(label, message, log_fn)
            if not kwargs.get("quiet", False):
                stamp = Cache.t_stamp()
                sys.stderr.write("{0} {1}: {2}\n".format(stamp, label, message))

    def debug(self, message, **kwargs: bool | int | str):
        """Log a debug message."""
        if self._level <= logging.DEBUG:
            kwargs[LABEL] = "DEBUG"
            self.log(message, **kwargs)

    def info(self, message, **kwargs: bool | int | str):  # noqa: WPS110
        """Log a info message."""
        if self._level <= logging.INFO:
            kwargs[LABEL] = "INFO"
            self.log(message, **kwargs)

    def warning(self, message, **kwargs: bool | int | str):
        """Log a warning message."""
        if self._level <= logging.WARNING:
            kwargs[LABEL] = WARNING
            self.log(message, **kwargs)

    def error(self, message, **kwargs: bool | int | str):
        """Log a error message."""
        if self._level <= logging.ERROR:
            kwargs[LABEL] = "ERROR"
            self.log(message, **kwargs)

    def critical(self, message, **kwargs: bool | int | str):
        """Log a critical message."""
        if self._level <= logging.CRITICAL:
            kwargs[LABEL] = "CRITICAL"
            self.log(message, **kwargs)
