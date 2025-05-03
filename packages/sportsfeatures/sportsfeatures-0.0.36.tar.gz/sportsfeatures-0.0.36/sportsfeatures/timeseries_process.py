"""Processing for time series features."""

# pylint: disable=duplicate-code,too-many-branches,too-many-nested-blocks

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

_LAGS = [1, 2, 4, 8]
_LAG_COLUMN = "lag"
_DAYS_COLUMN_SUFFIX = "days"
_ALL_SUFFIX = "all"
_COUNT_WINDOW_FUNCTION = "count"
_SUM_WINDOW_FUNCTION = "sum"
_MEAN_WINDOW_FUNCTION = "mean"
_MEDIAN_WINDOW_FUNCTION = "median"
_VAR_WINDOW_FUNCTION = "var"
_STD_WINDOW_FUNCTION = "std"
_MIN_WINDOW_FUNCTION = "min"
_MAX_WINDOW_FUNCTION = "max"
_SKEW_WINDOW_FUNCTION = "skew"
_KURT_WINDOW_FUNCTION = "kurt"
_SEM_WINDOW_FUNCTION = "sem"
_RANK_WINDOW_FUNCTION = "rank"
_WINDOW_FUNCTIONS = [
    _COUNT_WINDOW_FUNCTION,
    _SUM_WINDOW_FUNCTION,
    _MEAN_WINDOW_FUNCTION,
    _MEDIAN_WINDOW_FUNCTION,
    _VAR_WINDOW_FUNCTION,
    _STD_WINDOW_FUNCTION,
    _MIN_WINDOW_FUNCTION,
    _MAX_WINDOW_FUNCTION,
    _SKEW_WINDOW_FUNCTION,
    _KURT_WINDOW_FUNCTION,
    _SEM_WINDOW_FUNCTION,
    _RANK_WINDOW_FUNCTION,
]


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
            for feature_column in identifier.numeric_action_columns:
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
        for lag in _LAGS:
            lag_df = (
                original_identifier_df.shift(lag - 1)
                if lag != 1
                else original_identifier_df
            )
            for column in drop_columns:
                if column == dt_column:
                    continue
                feature_column = DELIMITER.join([column, _LAG_COLUMN, str(lag)])
                identifier_df[feature_column] = lag_df[column]

        for window in windows:
            window_df = (
                identifier_df.rolling(window, on=dt_column)
                if window is not None
                else identifier_df.expanding()
            )
            window_col = (
                str(window.days) + _DAYS_COLUMN_SUFFIX
                if window is not None
                else _ALL_SUFFIX
            )
            for column in drop_columns:
                if column == dt_column:
                    continue
                for window_function in _WINDOW_FUNCTIONS:
                    feature_column = DELIMITER.join(
                        [column, window_function, window_col]
                    )  # type: ignore
                    try:
                        if window_function == _COUNT_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].count()
                        elif window_function == _SUM_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].sum()
                        elif window_function == _MEAN_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].mean()
                        elif window_function == _MEDIAN_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].median()
                        elif window_function == _VAR_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].var()
                        elif window_function == _STD_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].std()
                        elif window_function == _MIN_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].min()
                        elif window_function == _MAX_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].max()
                        elif window_function == _SKEW_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].skew()
                        elif window_function == _KURT_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].kurt()
                        elif window_function == _SEM_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].sem()
                        elif window_function == _RANK_WINDOW_FUNCTION:
                            identifier_df[feature_column] = window_df[column].rank()
                        else:
                            raise ValueError(
                                f"Unrecognised window function: {window_function}"
                            )
                    except pd.errors.DataError as exc:
                        logging.warning(str(exc))
        identifier_ts[identifier_id] = (
            identifier_df.shift(1).drop(columns=drop_columns).copy()
        )

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

    # Write the columns to the dataframe ahead of time.
    relevant_columns = {dt_column}
    for identifier in identifiers:
        if (
            identifier.entity_type != EntityType.TEAM
            and identifier.entity_type == EntityType.PLAYER
        ):
            continue
        relevant_columns.add(identifier.column)
        for column in identifier.numeric_action_columns:
            relevant_columns.add(column)
            for lag in _LAGS:
                feature_column = DELIMITER.join([column, _LAG_COLUMN, str(lag)])
                relevant_columns.add(feature_column)
                df[feature_column] = None
            for window in windows:
                window_col = (
                    str(window.days) + _DAYS_COLUMN_SUFFIX
                    if window is not None
                    else _ALL_SUFFIX
                )
                for window_function in _WINDOW_FUNCTIONS:
                    feature_column = DELIMITER.join(
                        [column, window_function, window_col]
                    )
                    relevant_columns.add(feature_column)
                    df[feature_column] = None

    df_subset = df[list(relevant_columns)]
    identifier_ts: dict[str, pd.DataFrame] = _extract_identifier_timeseries(
        df_subset, identifiers, dt_column
    )
    identifier_ts = _process_identifier_ts(identifier_ts, windows, dt_column)
    df[list(relevant_columns)] = _write_ts_features(
        df_subset, identifier_ts, identifiers
    )
    return df[sorted(df.columns.values)].copy()
