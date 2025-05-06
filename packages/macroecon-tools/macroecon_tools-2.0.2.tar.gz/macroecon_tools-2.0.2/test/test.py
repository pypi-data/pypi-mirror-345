# import libraries
import unittest
import pandas as pd
import random

# get Timeseries class
import os, sys
script_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(script_dir, '..', 'src', 'macroecon_tools'))
import macroecon_tools as mt

class TestTimeseries(unittest.TestCase):
    def setUp(self):
        # Sample data for testing
        self.sample_data = pd.Series([i for i in range(24)], index=pd.date_range("2020-01-01", periods=24, freq="ME"))
        self.ts = Timeseries(self.sample_data, name="Sample", freq="monthly")

    def test_copy(self):
        ts_copy = self.ts.copy()
        # Assert that the copied instance is not the same as the original
        self.assertIsNot(ts_copy, self.ts)
        # Assert that the data and attributes of the copied instance are equal to the original
        self.assertTrue(ts_copy.equals(self.ts))
        self.assertEqual(ts_copy.name, self.ts.name)
        self.assertEqual(ts_copy.get_freqstr(), self.ts.get_freqstr())
        self.assertEqual(ts_copy.transformations, self.ts.transformations)

def test_print():
    sample_data = pd.Series([1, 2, 3, 4], index=pd.date_range("2020-01-01", periods=4, freq="ME"))
    ts = Timeseries(sample_data, name="Sample", source_freq="monthly")
    print(ts)
    large_sample_data = pd.Series([i for i in range(24)], index=pd.date_range("2020-01-01", periods=24, freq="ME"))
    ts = Timeseries(large_sample_data, name="Sample", source_freq="monthly")
    print(ts)

def test_agg():
    index = pd.date_range(start="2020-01-01", periods=36, freq="ME")
    data = Timeseries(pd.Series([i for i in range(36)], index=index), name="test")
    # print(data)
    data = data.aggregate('yearly', 'mean')
    print(f"{data}")

def test_pd_agg():
    index = pd.date_range(start="2020-01-01", periods=36, freq="ME")
    data = pd.Series([i for i in range(36)], index=index)
    data = data.resample('Y').mean()
    print(data)

def test_weekly():
    index = pd.date_range(start="2020-01-01", periods=36, freq="W")
    data = pd.Series([i for i in range(36)], index=index)
    print(Timeseries(data, name='test').aggregate('weekly', 'mean'))

def test_getdata():
    # Test get_fred
    data_sources = ['GDPC1', 'CPIAUCSL']
    data_names = ['GDP', 'CPI']
    data = fd.get_fred(data_sources, data_names)
    print(data)
    data.save(f'{script_dir}/test_data')

def test_load_data():
    # Load data
    data = TimeseriesTable().load(f'{script_dir}/test_data')
    print(f"{data}")

def test_dropna():
    index = pd.date_range(start="2020-01-01", periods=36, freq="ME")
    data = Timeseries(pd.Series([i for i in range(36)], index=index), name='test')
    data = data.dropna()
    print(data)

def test_table():
    index = pd.date_range(start="2020-01-01", periods=36, freq="ME")
    data = Timeseries(pd.Series([i for i in range(36)], index=index), name='test').aggregate('monthly', 'mean')
    table = TimeseriesTable()
    table['test'] = data
    print(table)

def test_pane_multi():
    PERIODS=12
    idx_one = pd.date_range(start="2010-01-01", periods=PERIODS, freq="ME")
    data_one = Timeseries(pd.Series([i for i in range(PERIODS)], index=idx_one), name='test_one').aggregate('monthly', 'mean')
    idx_two = pd.date_range(start="2010-01-01", periods=PERIODS, freq="ME")
    data_two = Timeseries(pd.Series([i*i for i in range(PERIODS)], index=idx_two), name='test_two').aggregate('monthly', 'mean')
    table = TimeseriesTable({
        'test_one': data_one,
        'test_two': data_two
    })
    idx_three = pd.date_range(start="2010-01-01", periods=PERIODS, freq="W-SUN")
    for idx in range(3):
        table[f"test_{idx}"] = Timeseries(pd.Series([i*i*i for i in range(PERIODS)], index=idx_three), name=f'test_{idx}').aggregate('weekly', 'mean')
    print(f"first table\n {table}\n")
    print(f"{table.corr()}")
    print(f"{table.to_latex()}")

def test_ts():
    data = pd.Series([1 + 0.3 * i for i in range(10)], index=pd.date_range('2024-01-01', periods=10))
    ts = Timeseries(data, name="Sample Data", source_freq="daily", data_source="Generated")

    # Apply transformations
    print(ts)
    log_diff = ts.logdiff(1)
    print(log_diff)
    truncated = ts.truncate('2024-01-01', '2024-01-04')
    print(truncated)

def test_corr():
    # generate panel
    PERIODS = 10
    panel = TimeseriesTable()
    for i in range(5):
        data = pd.Series([random.random() for i in range(PERIODS)], index=pd.date_range('2024-01-01', periods=PERIODS))
        ts = Timeseries(data, name=f"Sample Data {i}", source_freq="daily", data_source="Generated")
        panel[f"Data_{i}"] = ts
    # print(panel)
    # print()
    # print(panel.corr())
    # print()
    # print(panel.corr('Data_2', 'Data_1'))
    # print()
    # print(panel.corr('Data_2'))
    # print(panel.to_markdown())
    print(panel.corr("Data_1", "Data_4"))
    print(panel.corr("Data_4", "Data_1"))

def test_moments():
    # generate panel
    PERIODS = 10
    panel = TimeseriesTable()
    for i in range(5):
        data = pd.Series([i for i in range(PERIODS)], index=pd.date_range('2024-01-01', periods=PERIODS))
        ts = Timeseries(data, name=f"Sample Data {i}", source_freq="daily", data_source="Generated")
        panel[f"Data_{i}"] = ts
    print(panel.data_moments())

def test_tst_trunc():
    # Generate data
    PERIODS = 10
    panel = TimeseriesTable()
    for i in range(5):
        data = pd.Series([i for i in range(PERIODS)], index=pd.date_range('2024-01-01', periods=PERIODS, freq='ME'))
        ts = Timeseries(data, name=f"Sample Data {i}", source_freq="daily", data_source="Generated")
        panel[f"Data_{i}"] = ts
    # truncate
    print(panel.truncate('2024-01-01', '2024-01-04'))
    # reindex quarterly
    print(panel.reindex('Q', 'ffill'))

def test_tst_agg():
    # Generate data
    PERIODS = 10
    panel = TimeseriesTable()
    for i in range(5):
        data = pd.Series([i for i in range(PERIODS)], index=pd.date_range('2024-01-01', periods=PERIODS, freq='ME'))
        ts = Timeseries(data, name=f"Sample Data {i}", source_freq="daily", data_source="Generated")
        panel[f"Data_{i}"] = ts
    # aggregate
    print(panel.aggregate('quarterly', 'mean'))

def test_shift():
    # Generate data
    PERIODS = 10
    test_series = Timeseries(pd.Series([i for i in range(PERIODS)], index=pd.date_range('2024-01-01', periods=PERIODS, freq='ME')), name='Test Series')
    # shift
    print(test_series)
    print(test_series.diff(1))

def test_print_tst():
    # generate timeseriestable
    PERIODS = 100
    table = TimeseriesTable()
    for i in range(5):
        data = pd.Series([i for i in range(PERIODS)], index=pd.date_range('2024-01-01', periods=PERIODS))
        ts = Timeseries(data, name=f"Sample Data {i}", source_freq="daily", data_source="Generated")
        table[f"Data_{i}"] = ts
    print(table)

def test_default():
    print(mt.to_datetime("2025-03-02"))

if __name__ == '__main__':
    # test_agg()
    # test_pd_agg()
    # test_print()
    # unittest.main()
    # test_load_data()
    # test_load_data()
    # test_weekly()
    # test_dropna()
    # test_getdata()
    # test_table()
    # test_pane_multi()
    # test_ts()
    # test_corr()
    # test_moments()
    # test_tst_trunc()
    # test_tst_agg()
    # test_shift()
    # test_print_tst()
    test_default()
    