# Description: A set of fetch methods to get macroeconomic data

# Dependencies
from fredapi import Fred
import pandas as pd
from datetime import datetime, timedelta
import json
import pickle
# Used for downloading data from the internet
import requests
import zipfile
import tempfile
import shutil

# Get current directory
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Package imports
import timeseries as mt

# Directory for data cache
def get_cache_dir():
    return os.path.join(os.path.expanduser('~'), '.macro_cache')

def parse_year(year: str) -> datetime:
    '''
    Get year, month, day from %Y.%f
    '''
    year_int = int(year)
    month = int((year % 1) * 12) + 1
    day = int(((year % 1) * 12) % 1 * 30) + 1 
    return datetime(year_int, month, day)

def get_fred(data_sources: dict[str, str], start_date: str = "", end_date: str = "", api_key=None, force_fetch=False, verbose=False):
    '''
    Get data from FRED.

    Parameters
    ----------
    data_sources : dict[str, str] or list[str]
        Dictionary or list of FRED series IDs and names to assign to the data. If the value is None, the series ID is used as the name.
    date_one : str, optional
        Start date for data. Default is "".
    date_two : str, optional
        End date for data. Default is "".
    api_key : str, optional
        API key for FRED. Default is None (not needed if using cached data).
    force_fetch : bool, optional
        Force fetching data from FRED. Default is False.
    verbose : bool, optional
        Print verbose output. Default is False.

    Returns
    -------
    mt.TimeseriesTable
        Table of FRED data.
    
    Notes
    -----
    - Data is automatically set to year/quarter/month-end frequency and reindexed daily.
    - Caching is used to store data for one week before fetching new data from FRED (use force_fetch=True to ignore cache).
    '''
    try:
        # Look for api key 
        if api_key is None: # Load API key
            try:
                with open(f'{os.path.dirname(__file__)}/fred_api_key.txt') as f:
                    api_key = f.read().strip()
            except FileNotFoundError as e:
                try: 
                    api_key = os.environ['FRED_API_KEY']
                except KeyError as e:
                    pass # api_key is None
        
        # Create cache directory
        cache_dir = os.path.join(get_cache_dir(), 'fred_data')
        if not os.path.exists(cache_dir):
            print(f"Cache directory does not exist. Creating cache directory at {cache_dir}")
            os.makedirs(cache_dir)

        # Create connection to fred 
        if api_key:
            fred_connection = Fred(api_key=api_key)
        else:
            fred_connection = None
                
        # Results table
        data = mt.TimeseriesTable()

        # Get data from FRED
        current_series_id = None
        for series_id in data_sources:
            # map series_id to data_name
            if type(data_sources) == list:
                data_name = series_id
            elif type(data_sources) == dict:
                data_name = data_sources[series_id]
                if not data_name:
                    data_name = series_id
            else:
                raise ValueError("data_sources must be a list or dictionary.")
            
            # Log current series
            if verbose:
                print(f'Fetching data for {data_name} ({series_id})')
            current_series_id = series_id

            # Check if data is in cache
            cache_file = os.path.join(cache_dir, f"{series_id}.pkl")
            metadata_file = os.path.join(cache_dir, f"{series_id}_metadata.json")
            if not force_fetch and os.path.exists(cache_file) and os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    # Validation logic
                    cache_expiry = datetime.strptime(metadata['expiry_date'], '%Y-%m-%d')
                    if datetime.now() < cache_expiry:
                        # Read data from cache
                        with open(cache_file, 'rb') as f:
                            cached_data = pickle.load(f)
                        data[data_name] = cached_data
                        if verbose:
                            print(f"Data for {data_name} loaded from cache.\n")
                        continue
            
            # Get data from FRED (cache is expired or invalid)
            if fred_connection:
                raw_data = fred_connection.get_series(series_id)
                data_freq = fred_connection.get_series_info(series_id)['frequency']
            # Get data from FRED web page
            else: 
                # Add deprecation warning
                print("DeprecationWarning: Fetching data from FRED without an API key is deprecated. Please provide an API key to avoid this warning.", DeprecationWarning)
                page_url = f'https://fred.stlouisfed.org/series/{series_id}/downloaddata/{series_id}.csv'
                try:
                    raw_data = pd.read_csv(page_url, index_col='DATE', parse_dates=True)
                    # cast to pd.Series
                    raw_data = pd.Series(raw_data.squeeze()).dropna()
                except Exception as e:
                    raise ValueError(f"Error fetching data from FRED: {e}")
                # Try to infer frequency
                try:
                    data_freq =  pd.infer_freq(raw_data.index)
                except Exception as e:
                    raise ValueError(f"Error inferring frequency for {series_id}: {e}")
            
            # Save start and end dates
            start_date = raw_data.index[0]
            end_date = raw_data.index[-1]
            # Create timeseries
            new_data = mt.Timeseries(raw_data, name=data_name, source_freq=data_freq, data_source="FRED")
            # Save data to table
            data[data_name] = new_data
            if verbose:
                print(f"Data for {data_name} fetched from FRED.\n")

            # Save data to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(new_data, f)
            metadata = {
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'expiry_date': (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d'),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)

        return data
    
    except ValueError as e:
        if '404' in str(e):
            raise ValueError(f"Unable to fetch {series_id}. Check the series ID or try again with API key.")
        else:
            raise e
        
    except Exception as e:
        if force_fetch == False: # try again in case cache is old
            print(f"Error fetching {current_series_id} from FRED. Trying again with force_fetch=True.")
            return get_fred(data_sources, start_date, end_date, api_key, force_fetch=True)
        else:
            raise e

def get_barnichon(filepath: str, table: mt.TimeseriesTable, input_var: str, output_name: str):
    '''
    Get vacancy rate data from Barnichon.

    Parameters
    ----------
    filepath : str
        Path to Barnichon file.
    table : mt.TimeseriesTable
        Table to store data.
    input_var : str
        Input variable to use.
    output_name : str
        Name to assign to the output variable.

    Returns
    -------
    mt.TimeseriesTable
        Table with vacancy rate data.

    Notes
    -----
    - Data is automatically set to quarterly frequency.
    - Necessary data is automatically fetched from FRED if needed.
    '''
    # read data from barnichon file
    barnichon_data = pd.read_csv(filepath)
    barnichon_data['year'] = barnichon_data['year'].apply(parse_year)
    barnichon_data.set_index('year', inplace=True)
    barnichon_data = mt.TimeseriesTable(barnichon_data)

    match input_var: # construct data
        case 'V_LF':
            if 'JTSJOL' not in table:
                table['V'] = get_fred(['JTSJOL'], ['V'])['V']
            if 'CLF16OV' not in table:
                table['L'] = get_fred(['CLF16OV'], ['L'])['L']
            # Create vacancy rate with JOLTS data
            table[output_name] = mt.Timeseries(100 * table['V'] / table['L'], name=output_name, source_freq='Q', data_source='Barnichon')
            # Replace pre-2001 with Barnichon's vacancy rate
            input_data = barnichon_data.df.loc[:'2000-12-31'][input_var]
            for idx in input_data.index:
                if idx <= datetime(2000, 12, 31):
                    table[output_name][idx] = input_data[idx]
        case 'V_hwi':
            table[output_name] = mt.Timeseries(barnichon_data[input_var], name=output_name, source_freq='Q', data_source='Barnichon')
        case _:
            raise ValueError(f'Unknown input_var: {input_var}')
        
    return table

def get_ludvigson():
    '''
    Get macroeconomics uncertaintity data from Ludvigson.

    Returns
    -------
    dict
        Dictionary of TimeseriesTables for each data source (FinancialUncertainty, MacroUncertainty, RealUncertainty).

    Notes
    -----
    - Data is automatically set to monthly frequency.
    - Caching is used to store data for one week.
    '''
    # Define data source
    DATA_SOURCE = 'https://www.sydneyludvigson.com/s/MacroFinanceUncertainty_202408Update.zip'
    
    # Find the cache 
    cache_dir = os.path.join(get_cache_dir(), 'ludvigson_data')
    if not os.path.exists(cache_dir):
        print(f"Cache directory does not exist. Creating cache directory at {cache_dir}")
        os.makedirs(cache_dir)

    # Check if data is in cache
    data_files = ['FinancialUncertainty', 'MacroUncertainty', 'RealUncertainty']
    data = {}
    for data_file in data_files:
        cache_file = os.path.join(cache_dir, f"{data_file}.pkl")
        metadata_file = os.path.join(cache_dir, f"{data_file}_metadata.json")
        if os.path.exists(cache_file) and os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                cache_expiry = datetime.strptime(metadata['expiry_date'], '%Y-%m-%d')
                # Make sure the cache is still valid
                if datetime.now() < cache_expiry:
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                        data[data_file] = cached_data
                    print(f"Data for {data_file} loaded from cache.")
                    continue
    
    # Check if all data is in cache
    if len(data) == len(data_files):
        return data
    
    # Clear old files from the cache
    shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)
    # Download data from Ludvigson
    response = requests.get(DATA_SOURCE)
    zip_path = os.path.join(tempfile.gettempdir(), 'temp.zip')
    # Save the zip file to a temporary file
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    # Extract the contents of the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(cache_dir)

    # Parse the contents of the zip file
    file_names = os.listdir(cache_dir)
    for source_file in file_names:
        # Get the data
        data_name = [elem for elem in data_files if elem in source_file][0]
        data_path = os.path.join(cache_dir, source_file)
        src_data = pd.read_excel(data_path)
        # Construct TimeseriesTable
        table = mt.TimeseriesTable()
        # Set index
        src_data.set_index('Date', inplace=True)
        # Create timeseries
        for col in src_data.columns:
            table[col] = mt.Timeseries(src_data[col], name=col, source_freq='monthly', data_source='Ludvigson')
        data[data_name] = table
        # Save data to cache
        cache_file = os.path.join(cache_dir, f"{data_name}.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(table, f)
        metadata = {
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'expiry_date': (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')
        }
        metadata_file = os.path.join(cache_dir, f"{data_name}_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        print(f"Data for {data_name} fetched from Ludvigson.")
    
    return data
