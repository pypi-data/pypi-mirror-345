import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from src.macroecon_tools.timeseries import Timeseries

# FILE: Python/macroecon-tools/src/macroecon_tools/test_timeseries.py


class TestTimeseries(unittest.TestCase):

    def setUp(self):
        # Create sample data for Timeseries
        self.sample_data = pd.Series([i for i in range(24)], index=pd.date_range("2020-01-01", periods=24, freq="ME"))
        self.ts = Timeseries(self.sample_data, name='ts', source_freq='D')

    def test_initialization(self):
        self.assertIsInstance(self.ts, Timeseries)
        self.assertEqual(self.ts.name, 'ts')
        self.assertEqual(self.ts.source_freq, 'D')
        self.assertEqual(len(self.ts), 100)

    def test_logdiff(self):
        transformed_ts = self.ts.logdiff(1)
        self.assertIsInstance(transformed_ts, Timeseries)
        self.assertIn('logdiff_1_D', transformed_ts.transformations)

    def test_diff(self):
        transformed_ts = self.ts.diff(1)
        self.assertIsInstance(transformed_ts, Timeseries)
        self.assertIn('diff_1', transformed_ts.transformations)

    def test_log(self):
        transformed_ts = self.ts.log()
        self.assertIsInstance(transformed_ts, Timeseries)
        self.assertIn('log', transformed_ts.transformations)

    def test_log100(self):
        transformed_ts = self.ts.log100()
        self.assertIsInstance(transformed_ts, Timeseries)
        self.assertIn('log100', transformed_ts.transformations)

    def test_agg(self):
        aggregated_ts = self.ts.aggregate('monthly', 'mean')
        self.assertIsInstance(aggregated_ts, Timeseries)
        self.assertIn('agg_monthly_mean', aggregated_ts.transformations)

    def test_trunc(self):
        truncated_ts = self.ts.truncate('2020-01-10', '2020-01-20')
        self.assertIsInstance(truncated_ts, Timeseries)
        self.assertEqual(len(truncated_ts), 11)
        self.assertEqual(truncated_ts.index[0], pd.Timestamp('2020-01-10'))
        self.assertEqual(truncated_ts.index[-1], pd.Timestamp('2020-01-20'))

    def test_dropna(self):
        self.ts.iloc[0] = np.nan
        dropped_ts = self.ts.dropna()
        self.assertIsInstance(dropped_ts, Timeseries)
        self.assertEqual(len(dropped_ts), 99)

    def test_linear_filter(self):
        filtered_ts = self.ts.linear_filter('01-Jan-2020', '10-Jan-2020')
        self.assertIsInstance(filtered_ts, Timeseries)
        self.assertIn('linear_filter_2020-01-01_2020-01-10', filtered_ts.transformations)

    def test_hamilton_filter(self):
        filtered_ts = self.ts.hamilton_filter('01-Jan-2020', '10-Jan-2020')
        self.assertIsInstance(filtered_ts, Timeseries)
        self.assertIn('hamilton_filter_2020-01-01_2020-01-10_12_24', filtered_ts.transformations)

    def test_save_load(self):
        file_path = 'test_timeseries.pkl'
        self.ts.save(file_path)
        loaded_ts = Timeseries([]).load(file_path)
        self.assertEqual(len(loaded_ts), 100)
        self.assertEqual(loaded_ts.name, 'ts')
        self.assertEqual(loaded_ts.source_freq, 'D')

if __name__ == '__main__':
    unittest.main()