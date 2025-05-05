# dailylog

[![Build Status](https://github.com/wtfo-guru/dailylog-lib/workflows/dailylog_lib/badge.svg)](https://github.com/wtfo-guru/dailylog-lib/actions?query=workflow%3Adailylog_lib)
[![codecov](https://codecov.io/gh/wtfo-guru/dailylog-lib/branch/main/graph/badge.svg)](https://codecov.io/gh/wtfo-guru/dailylog-lib)
[![Python Version](https://img.shields.io/pypi/pyversions/dailylog-lib.svg)](https://pypi.org/project/dailylog-lib/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

## Overview

dailylog-lib is a minimal logger that will suppress all but first message in a specified
time to screen, while continuing to log messages to a specified log file. It also
provides standard debug, info, warning, error and critical methods.

## Installation

```bash

pip install dailylog-lib

```

## Usage

```python
# as a caching logger
from dailylog_lib.cache import Cache
logger = Cache()

# as a standard logger
from dailylog_lib.logger import Logger
logger = Logger()
```

## Documentation

- [Stable](https://dailylog-lib.readthedocs.io/en/stable)

- [Latest](https://dailylog-lib.readthedocs.io/en/latest)

## License

[MIT](https://github.com/wtfo-guru/dailylog-lib/blob/main/LICENSE)
