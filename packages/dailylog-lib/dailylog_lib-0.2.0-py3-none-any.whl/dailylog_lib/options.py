"""Top level module options for dailylog-lib."""

from pathlib import Path

from dailylog_lib.constants import DEFAULTS


class Options:
    """Class to manage the options."""

    _debug: int
    _test: bool
    _verbose: int
    cache_fn: str
    config_fn: str

    def __init__(self, **kwargs: bool | int | str) -> None:
        """
        Initialize the Options class with provided keyword arguments.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments that can include:
            - debug (bool | int): Debug level, defaults to 0.
            - test (bool): Test mode flag, defaults to False.
            - verbose (bool | int): Verbosity level, defaults to 0.
            - cache (str): Cache file path.
            - config (str): Config file path.

        The function ensures that cache and config file paths are absolute and
        valid, defaulting to specific paths if not provided.
        """
        self._debug = int(kwargs.get("debug", 0))
        self._test = bool(kwargs.get("test", False))
        self._verbose = int(kwargs.get("verbose", 0))
        key = "cache"
        self.cache_fn = Options.validate_fn_absolute(key, str(kwargs.get(key, "")))
        key = "config"
        self.config_fn = Options.validate_fn_absolute(key, str(kwargs.get(key, "")))

    def is_debug(self) -> bool:
        """Return True if debug option is greater than 0."""
        return self._debug > 0

    def is_test(self) -> bool:
        """Return True if test option is greater than 0."""
        return self._test

    def is_verbose(self) -> bool:
        """Return True if verbose option is greater than 0."""
        return self._verbose > 0

    @property
    def debug_level(self) -> int:
        """Return the debug level."""
        return self._debug

    @property
    def verbose_level(self) -> int:
        """Return the verbose level."""
        return self._verbose

    def config_path(self) -> Path:
        """Return the config file path."""
        return Path(self.config_fn)

    def cache_path(self) -> Path:
        """Return the cache file path."""
        return Path(self.cache_fn)

    @classmethod
    def validate_fn_absolute(cls, file_key: str, file_name: str) -> str:
        """Validate an absolute file name/path.

        Args:
            file_key (str): key name of file "config | cache"
            file_name (str): path name of file to validate

        Raises:
            ValueError: when file_name is empty string
            ValueError: when file_name is not absolute

        Returns:
            str: validate file name/path as a string
        """
        if file_name == "":
            file_name = str(DEFAULTS.get(file_key, ""))
            if file_name == "":
                raise ValueError("{0} path name cannot be empty".format(file_key))
        path = Path(file_name)
        if not path.is_absolute():
            raise ValueError("{0} path name must be absolute".format(file_key))
        return str(path)
