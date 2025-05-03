"""Atla package for PyPI distribution."""

from logfire import instrument, instrument_openai, trace

from ._main import configure, mark_failure, mark_success

__version__ = "0.0.1a0"

__all__ = [
    "configure",
    "instrument",
    "instrument_openai",
    "mark_failure",
    "mark_success",
    "trace",
]
