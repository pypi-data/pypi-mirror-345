# Macroecon-Tools
A open-source set of tools to assist with macroeconomic work. The package includes two classes, `Timeseries` and `TimeseriesTable`, for working with time series data and collections of time series. The package is built on `pandas` and `numpy` to offer additional metadata and advanced operations tailored for macroeconomic analysis of time series.

---

# Modules
- `timeseries`: Contains the datastructures extended from pd.Series and pd.DataFrame.
    - `Timeseries`: A class that extends pd.Series to include metadata and additional methods.
    - `TimeseriesTable`: A class that extends a dictionary and includes functionality from pd.DataFrame.
- `fetch_data`: Contains functions to fetch data from the internet.
    - `get_fred`: Fetches data from the Federal Reserve Economic Data (FRED) API.
    - `get_barnichon`: Fetches and parses data from the Barnichon dataset.
    - `get_ludvigson`: Fetches and parses data from the Ludvigson dataset.
- `visualizer`: Contains functions to visualize time series data.
    - `vis_multi_subplots`: Visualizes multiple time series on the same page using subplots.
    - `vis_two_vars`: Visualizes two variables as the x/y axes.
    - `vis_multi_lines`: Visualizes multiple lines on the same plot.

# Installation
To install the package, run the following command in the terminal:
```bash
pip install macroecon-tools
```

---

# Timeseries Module
## Timeseries Class
The `Timeseries` class extends the `pd.Series` class to include metadata and additional methods. The class is initialized with a `pd.Series` object and additional metadata. The additional metadata includes the following:
- `source_freq`: The frequency of the source data.
- `data_source`: The source of the data.
- `transformations`: A list of transformations applied to the data (automatically tracked).

The class also includes additional methods for working with time series data. Utility methods include:
- `save` and `load`: Methods to save and load the time series data into a pkl file.

Transformations include:
- `logdiff`: Computes the log difference of the time series.
- `diff`: Computes the difference of the time series.
- `log`: Computes the log of the time series.
- `log100`: Computes the log time 100 of the time series.
- `agg`: Aggregates the time series data by a specified frequency and method.
- `truncate`: Truncates the time series data by a specified start and end date.
- `dropna`: Drops missing values from the time series data.

Additional methods for filtering:
- `linear_filter`: Applies a linear filter to the time series data.
- `hamilton_filter`: Applies the Hamilton filter to the time series data.
- `hp_filter`: Applies the Hodrick-Prescott filter to the time series data.

## TimeseriesTable Class
The `TimeseriesTable` class extends a dictionary and includes functionality from `pd.DataFrame`. The class is initialized with a dictionary of `Timeseries` objects. The dataframe can be accessed with the .df property.

The class includes additional methods for working with collections of time series data. Utility methods include:
- `save` and `load`: Methods to save and load the time series data into a pkl file.
- `to_latex` and `to_markdown`: Methods to convert the time series data to a LaTeX table or Markdown table.
-  `corr`: Computes the correlation matrix of the time series data.
- `data_moments`: Computes the data moments of the specified variables of the time series data.

Additional methods for transformations:
- `truncate`: Truncates the time series data by a specified start and end date.
- `dropna`: Drops missing values from the time series data.
- `aggregate`: Aggregates the time series data by a specified frequency and method.