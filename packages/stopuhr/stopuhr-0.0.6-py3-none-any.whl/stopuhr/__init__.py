"""stopuhr: A simple tool for measuring durations in Python."""

import importlib.metadata

from stopuhr.chrono import Chronometer, stopwatch
from stopuhr.funkuhr import FunkUhr, funkuhr
from stopuhr.stopuhr import StopUhr, stopuhr

try:
    __version__ = importlib.metadata.version("stopuhr")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["Chronometer", "FunkUhr", "StopUhr", "funkuhr", "stopuhr", "stopwatch"]
