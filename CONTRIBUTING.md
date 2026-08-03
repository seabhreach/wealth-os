# Contributing to Wealth OS

## Prerequisites

Use Python 3.13 or newer and install the development dependencies:

```shell
python -m pip install -e ".[dev]"
pre-commit install
```

## Quality checks

Before opening a pull request, run:

```shell
pre-commit run --all-files
mypy
pytest
```

Keep changes scoped, fully typed, and covered by tests where behavior is introduced.
