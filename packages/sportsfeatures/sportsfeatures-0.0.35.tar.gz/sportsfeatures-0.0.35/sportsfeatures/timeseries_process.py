"""Processing for time series features."""

# pylint: disable=duplicate-code

import datetime
import functools
import logging
from warnings import simplefilter

import pandas as pd
from pandarallel import pandarallel  # type: ignore
from tqdm import tqdm

from .columns import DELIMITER
from .entity_type import EntityType
from .identifier import Identifier


def _extract_identifier_timeseries(
    df: pd.DataFrame, identifiers: list[Identifier], dt_column: str
) -> dict[str, pd.DataFrame]:
    tqdm.pandas(desc="Timeseries Progress")
    identifier_ts: dict[str, pd.DataFrame] = {}
    team_identifiers = [x for x in identifiers if x.entity_type == EntityType.TEAM]
    player_identifiers = [x for x in identifiers if x.entity_type == EntityType.PLAYER]
    relevant_identifiers = team_identifiers + player_identifiers

    def record_timeseries_features(row: pd.Series) -> pd.Series:
        nonlocal identifier_ts
        nonlocal relevant_identifiers

        for identifier in relevant_identifiers:
            if identifier.column not in row:
                continue
            identifier_id = row[identifier.column]
            if pd.isnull(identifier_id):
                continue
            key = DELIMITER.join([identifier.entity_type, identifier_id])
            df = identifier_ts.get(key, pd.DataFrame())
            df.loc[row.name, dt_column] = row[dt_column]  # type: ignore
            for feature_column in identifier.feature_columns:
                if feature_column not in row:
                    continue
                value = row[feature_column]
                if pd.isnull(value):
                    continue
                column = feature_column[len(identifier.column_prefix) :]
                if column not in df:
                    df[column] = None
                df.loc[row.name, column] = value  # type: ignore
            identifier_ts[key] = df.infer_objects()

        return row

    df.progress_apply(record_timeseries_features, axis=1)  # type: ignore
    return identifier_ts


def _process_identifier_ts(
    identifier_ts: dict[str, pd.DataFrame],
    windows: list[datetime.timedelta | None],
    dt_column: str,
) -> dict[str, pd.DataFrame]:
    # pylint: disable=too-many-locals
    for identifier_id in tqdm(identifier_ts):
        identifier_df = identifier_ts[identifier_id]
        original_identifier_df = identifier_df.copy()
        drop_columns = original_identifier_df.columns.values
        for window in windows + [1, 2, 4, 8]:
            if isinstance(window, int):
                lag_df = (
                    original_identifier_df.shift(window - 1)
                    if window != 1
                    else original_identifier_df
                )
                for column in original_identifier_df.columns.values:
                    if column == dt_column:
                        continue
                    feature_column = DELIMITER.join([column, "lag", str(window)])
                    identifier_df[feature_column] = lag_df[column]
            else:
                window_df = (
                    identifier_df.rolling(window, on=dt_column)
                    if window is not None
                    else identifier_df.expanding()
                )
                window_col = str(window.days) + "days" if window is not None else "all"
                for column in original_identifier_df.columns.values:
                    if column == dt_column:
                        continue
                    count_column = DELIMITER.join([column, "count", window_col])  # type: ignore
                    sum_column = DELIMITER.join([column, "sum", window_col])  # type: ignore
                    mean_column = DELIMITER.join([column, "mean", window_col])  # type: ignore
                    median_column = DELIMITER.join([column, "median", window_col])  # type: ignore
                    var_column = DELIMITER.join([column, "var", window_col])  # type: ignore
                    std_column = DELIMITER.join([column, "std", window_col])  # type: ignore
                    min_column = DELIMITER.join([column, "min", window_col])  # type: ignore
                    max_column = DELIMITER.join([column, "max", window_col])  # type: ignore
                    skew_column = DELIMITER.join([column, "skew", window_col])  # type: ignore
                    kurt_column = DELIMITER.join([column, "kurt", window_col])  # type: ignore
                    sem_column = DELIMITER.join([column, "sem", window_col])  # type: ignore
                    rank_column = DELIMITER.join([column, "rank", window_col])  # type: ignore
                    try:
                        identifier_df[count_column] = window_df[column].count()
                        identifier_df[sum_column] = window_df[column].sum()
                        identifier_df[mean_column] = window_df[column].mean()
                        identifier_df[median_column] = window_df[column].median()
                        identifier_df[var_column] = window_df[column].var()
                        identifier_df[std_column] = window_df[column].std()
                        identifier_df[min_column] = window_df[column].min()
                        identifier_df[max_column] = window_df[column].max()
                        identifier_df[skew_column] = window_df[column].skew()
                        identifier_df[kurt_column] = window_df[column].kurt()
                        identifier_df[sem_column] = window_df[column].sem()
                        identifier_df[rank_column] = window_df[column].rank()
                    except pd.errors.DataError as exc:
                        logging.warning(str(exc))
        identifier_ts[identifier_id] = identifier_df.shift(1).drop(columns=drop_columns)

    return identifier_ts


def _write_ts_features(
    df: pd.DataFrame,
    identifier_ts: dict[str, pd.DataFrame],
    identifiers: list[Identifier],
) -> pd.DataFrame:
    def write_timeseries_features(
        row: pd.Series,
        identifier_ts: dict[str, pd.DataFrame],
        identifiers: list[Identifier],
    ) -> pd.Series:
        for identifier in identifiers:
            if identifier.column not in row:
                continue
            identifier_id = row[identifier.column]
            if pd.isnull(identifier_id):
                continue
            key = DELIMITER.join([identifier.entity_type, identifier_id])
            if key not in identifier_ts:
                continue
            identifier_df = identifier_ts[key]
            identifier_row = identifier_df.iloc[0]
            for column in identifier_df.columns.values:
                new_column = identifier.column_prefix + column
                row[new_column] = identifier_row[column]
            identifier_ts[key] = identifier_df.iloc[1:]

        return row

    return df.progress_apply(
        functools.partial(
            write_timeseries_features,
            identifier_ts=identifier_ts,
            identifiers=identifiers,
        ),
        axis=1,
    )  # type: ignore


def timeseries_process(
    df: pd.DataFrame,
    identifiers: list[Identifier],
    windows: list[datetime.timedelta | None],
    dt_column: str,
) -> pd.DataFrame:
    """Process a dataframe for its timeseries features."""
    # pylint: disable=too-many-locals,consider-using-dict-items,too-many-statements,duplicate-code
    pandarallel.initialize(verbose=0)
    tqdm.pandas(desc="Progress")
    simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
    identifier_ts: dict[str, pd.DataFrame] = _extract_identifier_timeseries(
        df, identifiers, dt_column
    )
    identifier_ts = _process_identifier_ts(identifier_ts, windows, dt_column)
    return _write_ts_features(df, identifier_ts, identifiers)
