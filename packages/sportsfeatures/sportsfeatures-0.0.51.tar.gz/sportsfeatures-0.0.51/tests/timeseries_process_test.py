"""Tests for the timeseries process function."""
import datetime
import unittest
import os

import pandas as pd
from pandas.testing import assert_frame_equal

from sportsfeatures.timeseries_process import timeseries_process
from sportsfeatures.identifier import Identifier
from sportsfeatures.entity_type import EntityType


class TestTimeseriesProcess(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def test_timeseries_process(self):
        team_0_column_prefix = "teams/0"
        team_1_column_prefix = "teams/1"
        dt_column = "dt"
        team_0_id_column = team_0_column_prefix + "/id"
        team_0_kicks = team_0_column_prefix + "/kicks"
        team_0_id = "0"
        team_1_id_column = team_1_column_prefix + "/id"
        team_1_kicks = team_1_column_prefix + "/kicks"
        team_1_id = "1"
        df = pd.DataFrame(data={
            dt_column: [datetime.datetime(2022, 1, 1), datetime.datetime(2022, 1, 2), datetime.datetime(2022, 1, 3)],
            team_0_id_column: [team_0_id, team_1_id, team_0_id],
            team_0_kicks: [10.0, 20.0, 30.0],
            team_1_id_column: [team_1_id, team_0_id, team_1_id],
            team_1_kicks: [20.0, 40.0, 60.0],
        })
        identifiers = [
            Identifier(
                EntityType.TEAM,
                team_0_id_column,
                [team_0_kicks],
                team_0_column_prefix,
            ),
            Identifier(
                EntityType.TEAM,
                team_1_id_column,
                [team_1_kicks],
                team_1_column_prefix,
            ),
        ]
        ts_dfs = timeseries_process(df, identifiers, [datetime.timedelta(days=365), None], dt_column)
        expected_ts_dfs = pd.read_parquet(os.path.join(self.dir, "ts_df.parquet"))
        ts_dfs = ts_dfs[expected_ts_dfs.columns.values.tolist()]
        assert_frame_equal(expected_ts_dfs, ts_dfs)
