"""Tests for the process function."""
import datetime
import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from timeseriesfeatures.process import process


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def test_process(self):
        rows = 100
        df = pd.DataFrame(data={
            "feature1": [float(x) for x in range(rows)],
            "feature2": [float(x + 1) for x in range(rows)],
        }, index=[
            datetime.datetime(2022, 1, 1) + datetime.timedelta(x) for x in range(rows)
        ])
        features_df = process(df, windows=[None, datetime.timedelta(days=30)], lags=[1, 2, 4, 8])
        expected_features_df = pd.read_parquet(os.path.join(self.dir, "expected.parquet"))
        assert_frame_equal(features_df, expected_features_df)
