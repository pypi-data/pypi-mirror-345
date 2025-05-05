"""Top level module config for dailylog-lib."""

import os
from pathlib import Path

from wtforglib.dirs import ensure_directory
from wtforglib.files import load_yaml_file, write_yaml_file
from wtforglib.kinds import StrAnyDict

from dailylog_lib.exceptions import FilePermError
from dailylog_lib.options import Options

CURRENT_CONFIG_VERSION = 1
CONST_DEFAULT_LOG = str(Path.home() / "daily.log")


# WPS214 Found too many methods
class Config(Options):  # noqa: WPS214
    """Class to manage the configuration."""

    config: StrAnyDict

    def __init__(self, **kwargs: bool | int | str) -> None:
        """
        Initialize the Config class with provided keyword arguments.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments that can include:
            - debug (bool | int): Debug level, defaults to 0.
            - test (bool): Test mode flag, defaults to False.
            - verbose (bool | int): Verbosity level, defaults to 0.
            - cache (str): Cache file path.
            - config (str): Config file path.

        This constructor initializes the configuration by loading it from
        a file or creating a new configuration if no file exists.
        """
        super().__init__(**kwargs)
        if self.config_path().is_file():
            self.config = self._load_config()
        else:
            self.config = {}
            self.config["version"] = CURRENT_CONFIG_VERSION
            self.config["default_log"] = CONST_DEFAULT_LOG
            self._save_config()

    def set_default_log(self, log_fn: str) -> None:
        """Set the default log file.

        Parameters
        ----------
        log_fn : str
            Absolute path to the log file
        """
        log_path = Path(log_fn)
        Config.validate_path(log_path)
        self.config["default_log"] = str(log_path)
        self._save_config()

    @classmethod
    def update_config(cls, config: StrAnyDict) -> StrAnyDict:
        """Update configuration from version to current version.

        Args:
            config (StrAnyDict): previous config verstion
        """
        version = config.get("version", 0)
        if version != CURRENT_CONFIG_VERSION:
            raise ValueError("Unknown config version: {0}".format(version))
        return config

    @classmethod
    def validate_path(cls, path: Path) -> None:
        """Validate the file path exists or can be created.

        Args:
            path (Path): files spec for log

        Raises:
            FileNotFoundError: when parent directory doesn't exist or is not a directory
            FilePermError: when parent directory is not writable
        """
        if path.exists():
            Config.validate_existing_path(path)
        elif not path.parent.is_dir():
            raise FileNotFoundError("Directory not found: {0}".format(path.parent))
        elif not os.access(path.parent, os.W_OK):
            raise FilePermError("Not writable: {0}".format(path.parent))

    def default_log(self) -> str:
        """Returns the path to the default log.

        Returns
        -------
        str
            Path to the default log
        """
        return self.config.get("default_log", CONST_DEFAULT_LOG)

    @classmethod
    def validate_existing_path(cls, path: Path) -> None:
        """Validate existing path.

        Args:
            path (Path): files spec for log

        Raises:
            FileNotFoundError: when path exists but is not a file
            FilePermError: when path exists but is not writable
        """
        if not path.is_file():
            raise FileNotFoundError("Not a file: {0}".format(path))
        if not os.access(path, os.W_OK):
            raise FilePermError("Not writable: {0}".format(path))

    def _load_config(self) -> StrAnyDict:
        """Load configuration from file."""
        config = load_yaml_file(self.config_path())
        version = config.get("version", 0)
        if version != CURRENT_CONFIG_VERSION:
            return Config.update_config(config)
        return config

    def _save_config(self) -> None:
        """Save configuration to file."""
        if self.is_debug():
            print(  # noqa: WPS421
                "Saving configuration to file: {0}".format(self.config_path())
            )
        cfg_path = self.config_path()
        ensure_directory(cfg_path.parent)
        write_yaml_file(self.config_path(), self.config)
