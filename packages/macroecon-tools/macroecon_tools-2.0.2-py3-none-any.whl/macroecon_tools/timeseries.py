# Description: A class used to represent a timeseries object.

# Data processing
import pandas as pd
import numpy as np
# Timing
from datetime import datetime
from dateutil.relativedelta import relativedelta
# Filters
from quantecon._filter import hamilton_filter as qe_hamilton_filter
from scipy.signal import detrend
from statsmodels.tsa.filters.hp_filter import hpfilter
# Save/Load
import pickle

# Add path to constants
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import constants
from constants import Constants

# Documentation customization
__pdoc__ = {
    "Timeseries.transformations": None,
    "Timeseries.source_freq": None,
    "Timeseries.data_source": None,
    "Timeseries.label": None,
    "Timeseries.is_percent": None,
}

class Timeseries(pd.Series):
    r"""
    An extension of the Series class with customization for Timeseries purposes.
    """

    _metadata = ['name', 'label', 'source_freq', 'data_source', 'is_percent', 'transformations']

    def __init__(self, data, is_copy = False, name: str = None, label: str = "", source_freq: str = "unknown", data_source : str = "unknown", is_percent: bool = False, transformations: list[str] = [], *args, **kwargs):
        r"""
        Initializes a `Timeseries` object.

        ### Parameters
        - **data** (`pd.Series` or array-like):  
        A single variable in a time table.
        - **is_copy** (`bool`, optional):  
        If `True`, the data is treated as a copy and not reindexed to daily frequency. Default is `False`.
        - **name** (`str`, optional):  
        The name of the variable. Default is `None`.
        - **label** (`str`, optional):  
        The label of the variable used in visualizations. Default is the variable name.
        - **source_freq** (`str`, optional):  
        The frequency of the source data (e.g., `'quarterly'`, `'monthly'`, `'yearly'`). Default is `"unknown"`.
        - **data_source** (`str`, optional):  
        The source of the data. Default is `"unknown"`.
        - **is_percent** (`bool`, optional):  
        Indicates if the time series is a percent (used in visualizations). Default is `False`.
        - **transformations** (`list[str]`, optional):  
        A list of transformations applied to the data. Default is an empty list.
        - **\*args**:  
        Additional positional arguments passed to the `pd.Series` constructor.
        - **\*\*kwargs**:  
        Additional keyword arguments passed to the `pd.Series` constructor.

        ### Raises
        - **ValueError**: If the index is not a datetime index.
        - **ValueError**: If the variable name is not provided.
        - **ValueError**: If the frequency is not provided.

        ### Notes
        - The data is converted to `float64` type.
        - If `is_copy` is `False`, the data is reindexed to daily frequency.
        - The index is converted to a datetime index and its frequency is inferred.
        - Adding a new parameter also requires updating `_update()`.
        """

        # Make sure all data is valid
        if '.' in data:
            data = data.replace('.', np.nan)
        # convert data to float64
        data = pd.Series(data).dropna().astype('float64')
        # reindex the data to daily if not a copy
        if not is_copy:
            data = data.asfreq('D')
        # Call pd.Series constructor
        super().__init__(data, *args, **kwargs)

        # Metadata
        self.transformations = [val for val in transformations]
        self.source_freq = source_freq
        self.data_source = data_source

        # Ensure the index is a datetime index
        try:
            self.index = pd.to_datetime(self.index)
            # infer the frequency
            try:
                self.index.freq = pd.infer_freq(self.index)
            except Exception as e:
                print(f'Unable to infer frequency.\n{e}')
        except Exception as e:
            raise ValueError(f'Timeseries Class: Index must be a datetime index.\n{e}')
        
        # Check if need to rename
        if name:
            self.name = name
        if not self.name:
            raise ValueError('Timeseries Class: Variable name not provided')
        self.label = label if label else self.name # add the label attribute

        # Add is_percent
        self.is_percent = is_percent

    # copy constructor
    def _update(self, data: pd.Series, transformation: str = None, name: str = ""):
        """
        Updates the current `Timeseries` object with new data.

        ### Parameters
        - **data** (`pd.Series`):  
        The new data to update the `Timeseries` object with.
        - **name** (`str`, optional):  
        The name of the variable. If provided, it replaces the current name.
        - **transformation** (`str`, optional):  
        A transformation applied to the new data. If provided, it’s added to the list of transformations.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the updated data and transformations.
        """

        if transformation:
            self.transformations.append(transformation)
        if name:
            self.name = name
        return Timeseries(data, is_copy=True, name=self.name, label=self.label, source_freq=self.source_freq, data_source=self.data_source, is_percent=self.is_percent, transformations=self.transformations)

    def set_percent(self, is_percent: bool = True):
        """
        Sets the `Timeseries` object as a percent (used for TimeseriesVisualizer)

        ### Parameters
        - **is_percent** (`bool`, optional):  
        If `True`, the `Timeseries` object is marked as a percent. Default is `True`.
        """
        self.is_percent = is_percent
        return self
    
    def set_label(self, label: str):
        """
        Sets the label of the `Timeseries` object.

        ### Parameters
        - **label** (`str`):  
        The label to set for the `Timeseries` object.
        """
        self.label = label
        return self

    def __finalize__(self, other, method=None, **kwargs):
        r"""
        Propagates metadata from another `Timeseries` object to the current instance.

        ### Parameters
        - **other** (`Timeseries`):  
        The `Timeseries` object from which to propagate metadata.
        - **method** (`str`, optional):  
        The method used for propagation. Default is `None`.
        - **\*\*kwargs**:  
        Additional keyword arguments.

        ### Returns
        - **Timeseries**:  
        The `Timeseries` object with propagated metadata.
        """

        if isinstance(other, Timeseries):
            self.name = getattr(other, 'name', None)
            self.source_freq = getattr(other, 'source_freq', None)
            self.data_source = getattr(other, 'data_source', None)
            self.transformations = getattr(other, 'transformations', [])
        return self
    
    # getters
    def get_freqstr(self):
        r"""
        Returns the frequency of the `Timeseries`.

        ### Returns
        - **str**:  
        The frequency of the timeseries.
        """

        return self.index.freqstr
    
    # override string representation
    def __repr__(self):
        r"""
        Returns a string representation of the `Timeseries` object.

        ### Returns
        - **str**:  
        A string representation of the `Timeseries` object.
        """

        # create data display
        temp_data = self.copy().dropna()
        data = ""
        if len(temp_data) == 0:
            data = "Empty Timeseries\n"
        elif len(temp_data) <= 5:
            for i in range(len(temp_data)):
                data += f"{temp_data.index[i].strftime('%Y-%m-%d')}    {temp_data.iloc[i]}\n"
        else:
            n = 2
            # get the first n rows without the header
            for i in range(n):
                data += f"{temp_data.index[i].strftime('%Y-%m-%d')}    {temp_data.iloc[i]}\n"
            data += f"\t...\n"
            # get the last n rows
            for i in range(len(temp_data) - n, len(temp_data)):
                data += f"{temp_data.index[i].strftime('%Y-%m-%d')}    {temp_data.iloc[i]}\n"

        # build metadata
        metadata = f"Name: {self.name}, Freq: {self.dropna().get_freqstr()}, Length: {len(self.dropna())}"
        if self.source_freq:
            metadata += f", Source Freq: {self.source_freq}"
        if self.data_source:
            metadata += f", Data Source: {self.data_source}"
        metadata += "\n"
        
        # return string
        return (f"{data}"
                f"...\n"
                f"{metadata}"
                f"Transformations: {self.transformations}\n")  

    # save and load
    def save(self, file_path: str):
        r"""
        Saves the `Timeseries` to a file.

        ### Parameters
        - **file_path** (`str`):  
        The file path to save the `Timeseries` to.
        """

        # check if file path has pkl extension
        if 'pkl' not in file_path:
            if '.' in file_path:
                file_path = file_path.split('.')[0] + '.pkl'
            else:
                file_path += '.pkl'
        # save the timeseries to a file
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    def load(self, file_path):
        """
        Loads the `Timeseries` from a file.

        ### Parameters
        - **file_path** (`str`):  
        The file path to load the `Timeseries` from.
        """

        # check if file path has pkl extension
        if 'pkl' not in file_path:
            if '.' in file_path:
                file_path = file_path.split('.')[0] + '.pkl'
            else:
                file_path += '.pkl'
        # load the timeseries from a file
        with open(file_path, 'rb') as f:
            self = pickle.load(f) 
        return self

    # Override operators
    def __mul__(self, other):
        """
        Multiplies the data by a scalar.

        ### Parameters
        - **other** (`float`):  
        The scalar to multiply the data by.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the multiplied data.
        """

        # check if other is a scalar
        if not isinstance(other, (int, float)):
            if other.name is None:
                other_label = f"series_unknown"
            else:
                other_label = f"series_{other.name}"
        else:
            other_label = other
        return self._update(pd.Series(self) * other, f'multiply_{other_label}')

    def __truediv__(self, other):
        """
        Divides the data by a scalar.

        ### Parameters
        - **other** (`float`):  
        The scalar to divide the data by.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the divided data.
        """

        if not isinstance(other, (int, float)):
            if other.name is None:
                other_label = f"series_unknown"
            else:
                other_label = f"series_{other.name}"
        else:
            other_label = other
        return self._update(pd.Series(self) / other, f'divide_{other_label}')
    
    def __add__(self, other):
        """
        Adds the data to a scalar.

        ### Parameters
        - **other** (`float`):  
        The scalar to add to the data.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the added data.
        """

        if not isinstance(other, (int, float)):
            if other.name is None:
                other_label = f"series_unknown"
            else:
                other_label = f"series_{other.name}"
        else:
            other_label = other
        return self._update(pd.Series(self) + other, f'add_{other_label}')
    
    def __sub__(self, other):
        """
        Subtracts the data by a scalar.

        ### Parameters
        - **other** (`float`):  
        The scalar to subtract from the data.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the subtracted data.
        """

        if not isinstance(other, (int, float)):
            if other.name is None:
                other_label = f"series_unknown"
            else:
                other_label = f"series_{other.name}"
        else:
            other_label = other
        return self._update(pd.Series(self) - other, f'subtract_{other_label}')
    
    # Override right operators using operator overloading
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __rtruediv__(self, other):
        return self.__truediv__(other)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __rsub__(self, other):
        return self.__sub__(other)
    
    def parse_date(self, date: str) -> str:
        """
        Accepts multiple string formats and returns a date string in the format 'dd-mmm-yyyy'.

        ### Parameters
        - **date** (`str`):  
        The date string to parse.

        ### Returns
        - **str**:  
        The parsed date in the format 'dd-mmm-yyyy'.
        """

        if isinstance(date, datetime):
            return date.strftime('%d-%b-%Y')
        else:
            if '/' in date: # assume date is in the format 'mm/dd/yyyy'
                date = datetime.strptime(date, '%m/%d/%Y').strftime('%d-%b-%Y')
            elif '-' in date and len(date.split('-')[0]) == 4: # assume date is in the format 'yyyy-mm-dd'
                date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%Y')
            elif '-' in date and len(date.split('-')[1]) == 2: # assume date is in the format 'dd-mm-yyyy'
                print(f"Assuming {date} is formatted as 'mm-dd-yyyy'")
                date = datetime.strptime(date, '%d-%m-%Y').strftime('%d-%b-%Y')
            else:
                date = datetime.strptime(date, '%d-%b-%Y').strftime('%d-%b-%Y')
            return date

    # Transform data
    def logdiff(self, nlag: int, freq: str = None):
        """
        Transforms the data using the log difference method.

        ### Parameters
        - **nlag** (`int`):  
        The lag length for the transformation.
        - **freq** (`str`, optional):  
        Frequency of the original data. By default inferred from the series.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the transformed data.
        """

        trans_freq = self.get_freqstr() if not freq else freq
        annpp = Constants.annscale_map(trans_freq) / nlag
        return self._update(annpp * np.log(self / self.shift(nlag)), f'logdiff_{nlag}_{trans_freq}')
    
    def diff(self, nlag: int):
        """
        Transforms the data using the difference method.

        ### Parameters
        - **nlag** (`int`):  
        The lag length for the transformation.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the transformed data.
        """

        return self._update(pd.Series(self) - self.shift(nlag), f'diff_{nlag}')
    
    def log(self):
        """
        Transforms the data using the log method.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the transformed data.
        """

        return self._update(np.log(self), 'log')
    
    def log100(self):
        r"""
        Transforms the data using the 100x log method.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the transformed data.
        """

        return self._update(100 * np.log(self), 'log100')
    
    # Aggregation
    def aggregate(self, timestep: str, method: str):
        """
        Aggregates the data using the specified method.

        ### Parameters
        - **timestep** (`str`):  
        The timestep to aggregate the data (e.g., 'quarterly', 'monthly', 'yearly').
        - **method** (`str`):  
        The aggregation method to use (e.g., 'lastvalue', 'mean', 'sum').

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the aggregated data.
        """

        # Perform aggregation using super().resample and the specified aggregation method
        aggregated = pd.Series(getattr(super().resample(timestep), Constants.agg_map[method])()).dropna()
        # Update the current Timeseries object with the aggregated data
        if aggregated.index.freq is None:
            aggregated = aggregated.asfreq(timestep)
        # aggregated.index.freq = Constants.freq_map[timestep]
        return self._update(aggregated, f'agg_{timestep}_{method}')

    # Trunctate
    def truncate(self, date_one: str = "", date_two: str = ""):
        """
        Truncates the data between the specified dates.

        ### Parameters
        - **date_one** (`str`, optional):  
        The start date in 'dd-mmm-yyyy' format. Default is `""` (start of data).
        - **date_two** (`str`, optional):  
        The end date in 'dd-mmm-yyyy' format. Default is `""` (end of data).

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the truncated data.
        """

        # Check if date_one and date_two are provided
        if not date_one:
            date_one = self.index[0]
        if not date_two:
            date_two = self.index[-1]
        date_one = self.parse_date(date_one)
        date_two = self.parse_date(date_two)
        # update self data
        truncated_data = self[date_one: date_two]
        truncated_data.index = pd.to_datetime(truncated_data.index)
        # return the truncated data
        return self._update(truncated_data, f'trunc_{date_one}_{date_two}')

    def combine_other(self, data):
        """
        Replaces the data of the `Timeseries` object with the provided data.

        ### Parameters
        - **data** (`pd.Series`):  
        The data to replace the `Timeseries` object with.
        """
        
        # Go through index of data and replace
        for date in data.index: 
            self.loc[date] = data.loc[date]
        return self._update(self, f'replace_{data.name}')
    
    # Dropna
    def dropna(self, *args, **kwargs):
        """
        Drops missing values from the data.

        ### Returns
        - **Timeseries**:  
        A new `Timeseries` object with the missing values dropped.
        """

        return self._update(super().dropna(*args, **kwargs))

    # filters
    def linear_filter(self, date_one: str, date_two: str):
        """
        Filters the data using the linear method.

        Parameters
        ----------
        date_one : str
            The start date in the format 'dd-mmm-yyyy'.
        date_two : str
            The end date in the format 'dd-mmm-yyyy'.

        Returns
        -------
        Timeseries
            A new Timeseries object with the filtered data.
        """
        date_one = self.parse_date(date_one)
        date_two = self.parse_date(date_two)

        # Time range
        self = self.truncate(date_one, date_two)
        return self._update(detrend(self, axis=0, type='linear'), f'linear_filter_{date_one}_{date_two}')
    
    def hamilton_filter(self, date_one: str, date_two: str, lag_len: int = None, lead_len: int = None):
        """
        Filters the data using the Hamilton method.

        Parameters
        ----------
        date_one : str
            The start date in the format 'dd-mmm-yyyy'.
        date_two : str
            The end date in the format 'dd-mmm-yyyy'.
        lagLength : int, optional
            The lag length for the 'hamilton' filter. 
            Default is None (1 for yearly, 4 for quarterly, 12 for monthly).
        leadLength : int, optional
            The lead length for the 'hamilton' filter.
            Default is None (2 for yearly, 8 for quarterly, 24 for monthly).

        Returns
        -------
        Timeseries
            A new Timeseries object with the filtered data.

        Raises
        ------
        ValueError
            If the frequency is not supported for the 'hamilton' filter.
        """
        # get default lag and lead lengths
        if self.get_freqstr() in Constants.year_like:
            lag_len = 1
            lead_len = 2
        elif self.get_freqstr() in Constants.quarter_like:
            lag_len = 4
            lead_len = 8
        elif self.get_freqstr() in Constants.month_like:
            lag_len = 12
            lead_len = 24
        else:
            raise ValueError(f'{self.get_freqstr()} frequency not supported for Hamilton filter')
        
        # get the tstart 
        date_one_time = datetime.strptime(date_one, '%d-%b-%Y')
        if self.get_freqstr() in Constants.year_like:
            tstart = date_one_time - relativedelta(years=(lag_len + lead_len - 1))
        elif self.get_freqstr() in Constants.quarter_like:
            tstart = date_one_time - relativedelta(months=3*(lag_len + lead_len - 1))
        elif self.get_freqstr() in Constants.month_like:
            tstart = date_one_time - relativedelta(months=(lag_len + lead_len - 1))
        trham = self.truncate(tstart, date_two)
        # Get cyclical component 
        cycle, trend = qe_hamilton_filter(trham, lead_len, lag_len)
        cycle = pd.Series(cycle.flatten(), index=trham.index).dropna()
        trend = pd.Series(trend.flatten(), index=trham.index).dropna()
        return cycle, trend, lag_len, lead_len
    
    def hamilton_filter_detrend(self, date_one: str = "", date_two: str = "", lag_len: int = None, lead_len: int = None):
        """
        Filters the data using the Hamilton method.

        Parameters
        ----------
        date_one : str
            The start date in the format 'dd-mmm-yyyy'.
        date_two : str
            The end date in the format 'dd-mmm-yyyy'.
        lag_len : int, optional
            The lag length for the 'hamilton' filter. 
            Default is None (1 for yearly, 4 for quarterly, 12 for monthly).
        lead_len : int, optional
        """
        # Add default dates
        if not date_one:
            date_one = self.index[0]
            date_one = self.parse_date(date_one)
        if not date_two:
            date_two = self.index[-1]
            date_two = self.parse_date(date_two)
        # get cycle and trend
        cycle, trend, lag_len, lead_len = self.hamilton_filter(date_one, date_two, lag_len, lead_len)
        # update data
        return self._update(1 - (cycle / trend) * 100, f'hamilton_filter_detrend_{date_one}_{date_two}_{lag_len}_{lead_len}')

    def hp_filter(self, date_one: str = "", date_two: str = "", lamb: int = None):
        """
        Implements the hp (Hodrick-Prescott) filter.

        Parameters
        ----------
        date_one : str, optional
            The start date in the format 'dd-mmm-yyyy'. 
            Default is "" (start of data).
        date_two : str, optional
            The end date in the format 'dd-mmm-yyyy'.
            Default is "" (end of data).
        lamb : int, optional
            The smoothing parameter for the hp filter.
            Default is None (6.25 for yearly, 1600 for quarterly, 129600  for monthly).
        """
        # Parse dates
        if not date_one:
            date_one = self.index[0]
        if not date_two:
            date_two = self.index[-1]
        date_one = self.parse_date(date_one)
        date_two = self.parse_date(date_two)
        # Time range
        self = self.truncate(date_one, date_two)

        # Get default lambda
        if lamb:
            pass
        elif self.get_freqstr() in Constants.year_like:
            lamb = 6.25
        elif self.get_freqstr() in Constants.quarter_like:
            lamb = 1600
        elif self.get_freqstr() in Constants.month_like:
            lamb = 129600
        else:
            raise ValueError(f'{self.get_freqstr()} frequency not supported for HP filter')
        
        # Apply hp filter
        cycle, trend = hpfilter(self, lamb)
        return cycle, trend, lamb # cycle, trend
    
    def hp_filter_detrend(self, date_one: str = "", date_two: str = "", lamb: int = None):
        """
        Implements the hp (Hodrick-Prescott) filter.

        Parameters
        ----------
        date_one : str, optional
            The start date in the format 'dd-mmm-yyyy'. 
            Default is "" (start of data).
        date_two : str, optional
            The end date in the format 'dd-mmm-yyyy'.
            Default is "" (end of data).
        lamb : int, optional
            The smoothing parameter for the hp filter.
            Default is None (6.25 for yearly, 1600 for quarterly, 129600  for monthly).
        """
        # get cycle and trend
        cycle, trend, lamb = self.hp_filter(date_one, date_two, lamb)
        updated_data = pd.Series(cycle / trend, index=self.index).dropna()
        return self._update(updated_data, f'hp_filter_{date_one}_{date_two}_{lamb}')
    
    def __getattr__(self, name: str):
        """
        Tries to call the pd.Series method if the method is not found.

        Parameters
        ----------
        name : str
            The name of the method.

        Returns
        -------
        Timeseries
            A new Timeseries object with the default function applied.
        """
        try:
            # Directly fetch from pd.Series.__dict__ or pd.Series.__getattribute__
            attr = getattr(pd.Series, name)

            # Warn user
            print(f"Method '{name}' not found in Timeseries. Using default method from pd.Series.")

            # If it's a callable method, wrap it
            if callable(attr):
                def wrapper(*args, **kwargs):
                    result = attr(self, *args, **kwargs)
                    return self._update(result, f"apply_{name}")
                return wrapper

            # Otherwise return the raw attribute
            return attr
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
class TimeseriesTable(dict):
    """
    A custom TimeseriesTable that maintains a pd.DataFrame and a dictionary with Timeseries objects.
    """

    def __init__(self, data: dict | pd.DataFrame | None = {}, *args, **kwargs):
        """
        Initializes the TimeseriesTable. Ensures columns are Timeseries instances.

        Parameters
        ----------
        data : dict, pd.DataFrame, optional
            A dictionary where keys are column names and values are Timeseries instances or a pd.DataFrame.
        """
        # Handle pd.DataFrame
        if isinstance(data, pd.DataFrame):
            data = {col: Timeseries(data[col]) for col in data.columns}
        super().__init__(data, *args, **kwargs)

    # Update setitem
    def __setitem__(self, key, value):
        """
        Sets the item in the TimeseriesTable.

        Parameters
        ----------
        key : str
            The key to set.
        value : Timeseries
            The Timeseries object to set.
        """
        # update name of the Timeseries
        try:
            value = value._update(value, name=key)
        except AttributeError:
            raise ValueError('TimeseriesTable Class: Value must be a Timeseries object')
        # set the item
        super().__setitem__(key, value)

    def __getitem__(self, key):
        data = super().__getitem__(key).dropna()
        return data

    # Build DataFrame
    @property
    def df(self):
        """
        Returns the TimeseriesTable as a DataFrame.

        Returns
        -------
        pd.DataFrame
            A DataFrame representation of the TimeseriesTable.
        """
        # Reindex all columns to daily frequency
        return pd.concat({key: val.asfreq('D') for key, val in self.items()}, axis=1).dropna(how='all')

    # Length
    def __len__(self):
        """
        Returns the number of rows with some data.

        Returns
        -------
        int
            The length of the TimeseriesTable.
        """
        return len(self.df.dropna(how='all'))
    
    # Override attr
    def __getattr__(self, key):
        # if attribute not found try on the DataFrame
        try:
            return getattr(self.df, key)
        except AttributeError:
            raise AttributeError(f"Attribute '{key}' not found in TimeseriesTable")

    def __repr__(self):
        """
        Returns a string representation of the TimeseriesTable object. Displays the first/last two rows.
        """
        # show the first/last two rows
        with pd.option_context('display.max_rows', 4):
            return repr(self.df.dropna(how='all'))
    
    def to_latex(self):
        """
        Returns a LaTeX representation of the TimeseriesTable object.
        """
        return self.df.dropna(how='all').to_latex()
    
    def to_markdown(self):
        """
        Returns a Markdown representation of the TimeseriesTable object.
        """
        return self.df.dropna(how='all').to_markdown()
    
    # Utility
    def apply(self, func, *args, **kwargs):
        """
        Applies a function to the data.

        Parameters
        ----------
        func : function
            The function to apply to the data.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the function applied to the data.
        """
        return TimeseriesTable({key: func(val, *args, **kwargs) for key, val in self.items()})

    # truncate method
    def truncate(self, date_one: str = "", date_two: str = ""):
        """
        Truncates the data between the specified dates.

        Parameters
        ----------
        date_one : str, optional
            The start date in the format 'dd-mmm-yyyy'. Default is "" (start of data).
        date_two : str, optional
            The end date in the format 'dd-mmm-yyyy'. Default is "" (end of data).

        Returns
        -------
        TimeseriesTable
            A new TimeseriesTable object with the truncated data.
        
        Notes
        -----
            - Assumes that date parsing is handled by the Timeseries.truncate method.
        """
        # update self data
        return TimeseriesTable({key: val.truncate(date_one, date_two) for key, val in self.items()})

    # dropna method
    def dropna(self, *args, **kwargs):
        """
        Drops missing values from the data.

        Returns
        -------
        TimeseriesTable
            A new TimeseriesTable object with the missing values dropped.
        """
        return TimeseriesTable({key: val.dropna(*args, **kwargs) for key, val in self.items()})
    
    # reindex method
    def aggregate(self, timestep: str, method: str):
        """
        Aggregates the data using the specified method.

        Parameters
        ----------
        timestep : str
            The timestep to aggregate the data (e.g., 'quarterly', 'monthly', 'yearly').
        method: str
            The aggregation method to use (e.g., 'lastvalue', 'mean', 'sum').
        """
        return TimeseriesTable({key: val.aggregate(timestep, method) for key, val in self.items()})

    # correlation
    def corr(self, var_one: str = "", var_two: str = ""):
        """
        Returns the correlation matrix of the data.

        Parameters
        ----------
        var_one : str, optional
            The first variable to compute the correlation matrix. Default is "".
        var_two : str, optional
            The second variable to compute the correlation matrix. Default is "".

        Returns
        -------
        pd.DataFrame
            A DataFrame with the correlation matrix.

        Notes
        -----
            - If `var_one` and `var_two` are provided, the correlation between the two variables is returned.
            - If only `var_one` is provided, the correlation between `var_one` and all other variables is returned.
        """
        if var_one and var_two:
            return self.df[var_one].corr(self.df[var_two])
        elif var_one:
            return self.df.corrwith(self.df[var_one])
        else:
            return self.df.corr()
        
    # generate requested moments of table
    @staticmethod
    def apply_moment_func(data: Timeseries, moment: str):
        """
        Computes the specified statistical moment for a given Timeseries.

        Parameters
        ----------
        data : Timeseries
            The data to compute the moment on.
        moment : str
            The statistical moment to compute. Options are 'mean', 'SD', 'Skew', 'Kurt', 'min', 'max'.

        Returns
        -------
        pd.Series
            A new Series object with the computed moment.

        Raises
        ------
        ValueError
            If the specified moment is not available.
        """
        if moment == 'mean':
            return data.mean()
            # return lambda X: np.nanmean(X, axis=0)
        elif moment == 'SD':
            return data.std()
            # return lambda X: np.nanstd(X, axis=0, ddof=1)
        elif moment == 'Skew':
            return data.skew()
            # return lambda X: skew(X, axis=0, nan_policy='omit', bias=False)
        elif moment == 'Kurt':
            return data.kurt()
            # return lambda X: kurtosis(X, axis=0, nan_policy='omit', bias=False)
        elif moment == 'min':
            return data.min()
            # return lambda X: np.nanmin(X, axis=0)
        elif moment == 'max':
            return data.max()
            # return lambda X: np.nanmax(X, axis=0)
        else:
            raise ValueError('Moment not available')

    def data_moments(self, vars: list[str] = [], moments: list[str] = []):
        """
        Computes specified statistical moments for given variables in a dataset.

        Parameters
        ----------
        vars : list of str
            The list of variable names for which to display the moments. Default is an empty list (all variables).
        moments : list of str
            The list of moments to compute. Options are 'mean', 'SD', 'Skew', 'Kurt', 'min', 'max'. Default is an empty list (all moments).

        Returns
        -------
        None
            Prints the table of computed moments for the specified variables.
        """
        # Parse input
        if len(vars) == 0:
            vars = self.df.columns
        if len(moments) == 0:
            moments = ['mean', 'SD', 'Skew', 'Kurt', 'min', 'max']

        # Create empty table
        moments_table = pd.DataFrame()

        # Compute moments and append to table
        for moment in moments:
            # apply each fun to the columns 
            vals = []
            for col in vars:
                vals.append(TimeseriesTable.apply_moment_func(self.df[col], moment))
            # append vals as a new row to momtab
            moments_table = pd.concat([moments_table, pd.DataFrame([vals])], ignore_index=True)
        
        # Round and add row labels
        def format_numbers(x):
            return f"{x:.3f}"
        moments_table = moments_table.map(format_numbers)
        moments_table.columns = self.df[vars].columns
        moments_table.index = moments

        # Display table
        return moments_table
    
    # save and load
    def save(self, file_path):
        '''
        Saves the TimeseriesTable to a file.

        Parameters
        ----------
        file_path : str
            The file path to save the TimeseriesTable to.
        '''
        # check if file path has pkl extension
        if 'pkl' not in file_path:
            if '.' in file_path:
                file_path = file_path.split('.')[0] + '.pkl'
            else:
                file_path += '.pkl'
        # save the TimeseriesTable to a file
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    def load(self, file_path):
        '''
        Loads the TimeseriesTable from a file.

        Parameters
        ----------
        file_path : str
            The file path to load the TimeseriesTable from.
        '''
        # check if file path has pkl extension
        if 'pkl' not in file_path:
            if '.' in file_path:
                file_path = file_path.split('.')[0] + '.pkl'
            else:
                file_path += '.pkl'
        # load the TimeseriesTable from a file
        with open(file_path, 'rb') as f:
            self = pickle.load(f)
        return self
    
if __name__ == '__main__':
    # List all methods in timeseriestable
    print([func for func in dir(TimeseriesTable) if callable(getattr(TimeseriesTable, func)) and not func.startswith("__")])