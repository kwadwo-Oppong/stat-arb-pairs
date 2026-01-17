"""
Pairs trading research project - core modules.
"""

__version__ = "0.1.0"

from . import data
from . import tests
from . import signals
from . import backtest
from . import metrics

__all__ = ["data", "tests", "signals", "backtest", "metrics"]
