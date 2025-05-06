"""Bare-bones Python package to access LEGEND test data files."""

from legendtestdata._version import version as __version__
from legendtestdata.core import LegendTestData

__all__ = ["__version__", "LegendTestData"]
