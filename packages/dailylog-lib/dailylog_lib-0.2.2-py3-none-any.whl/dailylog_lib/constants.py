"""Top level module constants for dailylog-lib."""

import types
from pathlib import Path

VERSION = "0.2.2"

HOME = Path.home()
DEFAULTS = types.MappingProxyType(
    {
        "cache": HOME / ".cache" / "dailylog.json",
        "config": HOME / ".config" / "dailylog.yaml",
    }
)
