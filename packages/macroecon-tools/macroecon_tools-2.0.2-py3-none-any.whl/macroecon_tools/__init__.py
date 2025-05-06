# Get current directory
# import os, sys
# dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(dir_path)

r"""
Initialization for the `macroecon-tools` package.

### Imports from submodules:

- **`timeseries`**
  - `Timeseries`
  - `TimeseriesTable`

- **`fetch_data`**
  - `get_fred()`
  - `get_barnichon()`
  - `get_ludvigson()`

- **`TimeseriesVisualizer`**
  - `subplots()`
  - `two_vars()`
  - `multi_lines()`
"""

# import submodules
from .timeseries import *
from .fetch_data import *
from .visualizer import *

# add default to pandas
import pandas as pd
__all__ = ['Timeseries', 'TimeseriesTable', 'TimeseriesVisualizer', 'get_fred', 'get_barnichon', 'get_ludvigson', 'pd']

def __getattr__(name):
    """
    Default to pandas if attribute not found.
    """
    if hasattr(pd, name):
        return getattr(pd, name)
    raise AttributeError(f"module 'macroecon_tools' has no attribute '{name}'")
