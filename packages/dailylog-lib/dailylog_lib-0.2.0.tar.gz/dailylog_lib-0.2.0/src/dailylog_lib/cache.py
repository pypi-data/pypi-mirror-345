"""Top level module cache for dailylog-lib."""

import sys
from datetime import datetime, timezone
from typing import Dict, Optional

from wtforglib.dirs import ensure_directory
from wtforglib.files import load_json_file, write_json_file
from wtforglib.kinds import StrAnyDict

from dailylog_lib.config import Config

CONST_CACHE_VERSION = 1
CONST_DAY = 86400


class CacheRecord:
    """Class representing a cache record."""

    shown: int
    suppressed: int

    def __init__(self, d_obj: Optional[Dict[str, int]] = None) -> None:
        """Class constructor.

        Parameters
        ----------
        d_obj : Dict[str, int], optional
            Cache record object, by default None
        """
        if d_obj is None:
            self.shown = 0
            self.suppressed = 0
            return
        self._from_dict(d_obj)

    def suppress(self, stifle: int) -> bool:
        """Suppress display of cache record.

        Parameters
        ----------
        stifle : int
            Suppress if last display is > stifle seconds

        Returns
        -------
        bool
            True if suppressed
        """
        now = int(datetime.now(timezone.utc).timestamp())
        if now - self.shown > stifle:
            self.shown = now
            self.suppressed = 0
            return False
        self.suppressed += 1
        return True

    def to_dict(self) -> Dict[str, int]:
        """Convert instance to dict.

        Returns
        -------
        Dict[str, int]
            Instance data as dict
        """
        return {"shown": self.shown, "suppressed": self.suppressed}

    def _from_dict(self, d_obj: Dict[str, int]) -> None:
        """Assign instance data from dict.

        Parameters
        ----------
        d_obj : Dict[str, int]
            Record data
        """
        self.shown = d_obj.get("shown", 0)
        self.suppressed = d_obj.get("suppressed", 0)


class Cache(Config):
    """Class to manage the cache."""

    cache: StrAnyDict

    def __init__(self, **kwargs: bool | int | str) -> None:
        """
        Initialize the Cache class with provided keyword arguments.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments that can include:
            - debug (bool | int): Debug level, defaults to 0.
            - test (bool): Test mode flag, defaults to False.
            - verbose (bool | int): Verbosity level, defaults to 0.
            - cache (str): Cache file path.
            - config (str): Config file path.

        This constructor initializes the cache by loading it from a file or creating
        a new cache if no file exists.
        """
        super().__init__(**kwargs)
        self._load_cache()

    def log_message(self, key: str, message: str, **kwargs) -> bool:
        """Log a message with specified parameters, handling suppression and caching.

        Parameters
        ----------
        key : str
            Unique key for the cache record.
        message : str
            The message to log.
        **kwargs : dict
            Additional keyword arguments:
                - label (str): Log level label, defaults to "ERROR".
                - logfn (str): Path to the log file, defaults to the default log.
                - quiet (bool): If True, suppresses terminal output.
                - suppress (int): Number of seconds to suppress repeated messages,
                  defaults to CONST_DAY.

        Returns
        -------
        bool
            True if the message was logged to the terminal or cache was updated,
            False otherwise.
        """
        rtn_val = False
        label = kwargs.get("label", "ERROR")
        log_fn = kwargs.get("logfn", self.default_log())
        if kwargs.get("quiet", False):
            Cache.append_daily(label, message, log_fn)
            rtn_val = True
        else:
            record: CacheRecord = self._get_record(key)
            if not record.suppress(kwargs.get("suppress", CONST_DAY)):
                sys.stderr.write("{0}: {1}\n".format(label, message))
                rtn_val = True
            Cache.append_daily(label, message, log_fn, record.suppressed)
            self.cache["entries"][key] = record.to_dict()
            self._save_cache()
        return rtn_val

    @classmethod
    def t_stamp(cls) -> str:
        """Return current time stamp."""
        # WPS323 Found `%` string formatting
        fmt = "%a %b %d %H:%M:%S %p %Z %Y"  # noqa: WPS323
        return datetime.now(timezone.utc).astimezone().strftime(fmt)

    @classmethod
    def append_daily(
        cls,
        label: str,
        message: str,
        log_fn: str,
        s_cnt: Optional[int] = None,
    ) -> None:
        """Append a message to the specified log file.

        Parameters
        ----------
        label : str
            Log level label DEBUG, INFO, WARNING, ERROR ...
        message : str
            Record to log
        log_fn : str
            Path name of log file
        s_cnt : int
            Number of seconds to suppress screen output.
        """
        stamp = Cache.t_stamp()
        with open(log_fn, "a") as daily_log:
            if s_cnt is None:  # no suppressed count
                daily_log.write("{0} {1}: {2}\n".format(stamp, label, message))
            else:
                daily_log.write(
                    "{0} {1}: {2} [{3}]\n".format(stamp, label, message, s_cnt),
                )
            daily_log.close()

    def _get_record(self, key: str) -> CacheRecord:
        """Get cache record.

        Parameters
        ----------
        key : str
            unique key for record

        Returns
        -------
        CacheRecord
            The record
        """
        entries = self.cache.get("entries", {})
        return CacheRecord(entries.get(key, None))

    def _load_cache(self) -> None:
        """Load cache from file if it exists otherwise create a cache."""
        cache_path = self.cache_path()
        if cache_path.is_file():
            self.cache = load_json_file(cache_path)
        else:
            self.cache = {}
            self.cache["version"] = CONST_CACHE_VERSION
            self.cache["entries"] = {}
            self._save_cache()

    def _save_cache(self) -> None:
        """Save cache to file."""
        cache_path = self.cache_path()
        ensure_directory(cache_path.parent)
        write_json_file(cache_path, self.cache)
