# tk-core

[![PyPI Latest Release](https://img.shields.io/pypi/v/tk-core.svg)](https://pypi.org/project/tk-core/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Centralized core functionality for Terakeet SD, DS, DE, etc.

## Installation

The tk-core package is available on PyPI and can be installed using pip:

```
pip install tk-core
```

# APIs

## Current

- [common](src/tk_core/common/README.md)
  - anything you find yourself using frequently could be added here
- [serp_api](src/tk_core/serp_api/README.md)
  - anything related to <a href=https://serpapi.com>SERPAPI</a>
  - there is a base class for all Google endpoints: `serp_api.base.py:SERPAPI`
- [snowflake](src/tk_core/snowkeet/README.md)
  - anything related to snowflake
- [core](src/tk_core/core/README.md)
  - functionality that is core to the other sub-modules in the package
- [async module](src/tk_core/core/async_module/README.md)
  - helper functions and async functionality that is core to the other sub-modules in the package

## Future

- google
- open_ai
- semrush

## Examples

Each sub-packages should have their own directory inside the `examples` directory. These will be built out over time to help (along with the documentation) understand functionality and common use cases for the tk-core package.

# Project Structure

```
tk-core
|
├── src
│   └── tk_core
│       ├── common
│       │   ├── de_service.py
│       │   ├── dictionary.py
│       │   ├── files.py
│       │   ├── hasher.py
│       │   └── s3.py
|       |   |__ timeout.py
|       |
│       ├── core
│       │   └── models.py
|       |
│       ├── google (future)
│       │   ├── gsc.py
│       │   ├── ga.py
│       │   ├── sheets.py
│       │   ├── calendar.py
│       │   └── gmail.py
|       |
│       ├── open_ai (future)
|       |
│       ├── semrush (future)
|       |
│       ├── serp_api
│       │   ├── README.md
│       │   ├── base.py
│       │   ├── batch_serp.py
│       │   ├── format_for_snowflake.py
│       │   ├── models.py
│       │   ├── serp.py
│       │   ├── trend.py
│       │   └── util.py
|       |
│       └── snowflake
│       │   ├── error_wrapper.py
│       │   ├── snowkeet_new.py
│           └── snowkeet.py
└── test
    ├── common
    ├── core
    └── serpapi
|
├── README.md
├── .coveragerc
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
```


# Questions, Concerns, Bugs

Clone the repo, create a PR and give it a shot your self. Make sure to write some tests--or update the existing ones--with any changing functionality. Feel free to reach out to the engineering team for help.
