"""
Package initialization and public API exports for netviz_tools.

This package includes three main classes: DataManager, TradeNetwork, and TradeSeries.
- DataManager: Handles the loading and processing of trade data.
- TradeNetwork: Represents a trade network and provides methods for analysis and visualization.
- TradeSeries: Represents a time series of trade data and provides methods for analysis and visualization.
"""

try:
    # Python 3.8+
    from importlib.metadata import version as _get_version
except ImportError:
    # Python <3.8
    from importlib_metadata import version as _get_version

__version__ = _get_version("netviz_tools")
__author__ = "Tyson Johnson"
__email__  = "tjohns94@gmu.edu"
__license__ = "MIT"

from .data_manager import DataManager
from .trade_network import TradeNetwork
from .trade_series import TradeSeries
from .utils import save_json, CONTINENT_COLORS

__all__ = [
    "DataManager",
    "TradeNetwork",
    "TradeSeries",
    "save_json",
    "CONTINENT_COLORS",
]
