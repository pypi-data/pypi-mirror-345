"""Processing for time series features."""

# pylint: disable=duplicate-code,too-many-branches,too-many-nested-blocks,too-many-locals,too-many-statements

import datetime

import pandas as pd
import polars as pl
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
_ROW_IDX_COLUMN = "row_idx"
_COLUMN_PREFIX_COLUMN = "column_prefix"


def timeseries_process(
    df: pd.DataFrame,
    identifiers: list[Identifier],
    windows: list[datetime.timedelta | None],
    dt_column: str,
) -> pd.DataFrame:
    """Process a dataframe for its timeseries features."""

    pl_df = pl.from_pandas(df)
    pl_df = pl_df.with_row_count(_ROW_IDX_COLUMN)
    for entity_type in [EntityType.TEAM, EntityType.PLAYER]:
        entity_identifiers = [x for x in identifiers if x.entity_type == entity_type]
        # Find all the unique identifiers
        unique_ids = set()
        for identifier in entity_identifiers:
            unique_ids.update(pl_df[identifier.column].unique().to_list())
        for unique_id in tqdm(unique_ids, desc=f"Processing {entity_type} time series"):
            # For each unique identifier, isolate their features into their respective columns
            identifier_dfs = []
            all_expected_cols = set()
            for identifier in entity_identifiers:
                cols = [
                    x for x in identifier.numeric_action_columns if x in pl_df.columns
                ]
                col_map = {x: x[len(identifier.column_prefix) :] for x in cols}
                identifier_df = (
                    pl_df.filter(pl.col(identifier.column) == unique_id)
                    .rename(col_map)
                    .select(
                        pl.col(list(col_map.values()) + [dt_column, _ROW_IDX_COLUMN])
                    )
                )
                identifier_df = identifier_df.with_columns(
                    pl.lit(identifier.column_prefix).alias(_COLUMN_PREFIX_COLUMN)
                )
                identifier_dfs.append(identifier_df)
                all_expected_cols.update(identifier_df.columns)
                all_expected_cols.add(_COLUMN_PREFIX_COLUMN)
            identifier_dfs = [
                x.with_columns(
                    pl.lit(None).alias(col)
                    for col in all_expected_cols
                    if col not in x.columns
                ).select(all_expected_cols)
                for x in identifier_dfs
            ]
            id_df = pl.concat(identifier_dfs).sort(dt_column)
            # Perform time series on these features
            for window in windows:
                window_col = (
                    str(window.days) + _DAYS_COLUMN_SUFFIX
                    if window is not None
                    else _ALL_SUFFIX
                )
                agg_funcs = []
                window_cols = set()
                for window_func in _WINDOW_FUNCTIONS:
                    for col in all_expected_cols:
                        if col in {dt_column, _ROW_IDX_COLUMN, _COLUMN_PREFIX_COLUMN}:
                            continue
                        feature_column = DELIMITER.join([col, window_func, window_col])
                        if window_func == _COUNT_WINDOW_FUNCTION:
                            agg_funcs.append(pl.len().alias(feature_column))
                        elif window_func == _SUM_WINDOW_FUNCTION:
                            agg_funcs.append(pl.sum(col).alias(feature_column))
                        elif window_func == _MEAN_WINDOW_FUNCTION:
                            agg_funcs.append(pl.mean(col).alias(feature_column))
                        elif window_func == _MEDIAN_WINDOW_FUNCTION:
                            agg_funcs.append(pl.median(col).alias(feature_column))
                        elif window_func == _VAR_WINDOW_FUNCTION:
                            agg_funcs.append(pl.var(col).alias(feature_column))
                        elif window_func == _STD_WINDOW_FUNCTION:
                            agg_funcs.append(pl.std(col).alias(feature_column))
                        elif window_func == _MIN_WINDOW_FUNCTION:
                            agg_funcs.append(pl.min(col).alias(feature_column))
                        elif window_func == _MAX_WINDOW_FUNCTION:
                            agg_funcs.append(pl.max(col).alias(feature_column))
                        elif window_func == _SKEW_WINDOW_FUNCTION:
                            agg_funcs.append(pl.col(col).skew().alias(feature_column))
                        elif window_func == _KURT_WINDOW_FUNCTION:
                            agg_funcs.append(
                                pl.col(col).kurtosis().alias(feature_column)
                            )
                        elif window_func == _SEM_WINDOW_FUNCTION:
                            agg_funcs.append(
                                (pl.std(col) / pl.len().sqrt()).alias(feature_column)
                            )
                        elif window_func == _RANK_WINDOW_FUNCTION:
                            agg_funcs.append(pl.col(col).rank().alias(feature_column))
                        else:
                            raise ValueError(
                                f"Unrecognised window function: {window_func}"
                            )
                        window_cols.add(feature_column)
                win_df = id_df
                if window is not None:
                    win_df = id_df.rolling(index_column=dt_column, period=window).agg(
                        agg_funcs
                    )
                else:
                    win_df = win_df.select(agg_funcs)
                win_df = win_df.with_columns(
                    [pl.col(col).shift(1) for col in window_cols]
                )
                win_df = win_df.with_columns(id_df[_ROW_IDX_COLUMN])
                if dt_column in win_df.columns:
                    win_df = win_df.drop(dt_column)
                id_df = id_df.join(win_df, on=_ROW_IDX_COLUMN, how="left")
                existing_right_cols = [
                    col for col in window_cols if f"{col}_right" in id_df.columns
                ]
                id_df = id_df.with_columns(
                    [
                        pl.coalesce([pl.col(f"{col}_right"), pl.col(col)]).alias(col)
                        for col in existing_right_cols
                    ]
                ).drop(existing_right_cols)
            for lag in _LAGS:
                id_df = id_df.with_columns(
                    [
                        pl.col(col)
                        .shift(lag)
                        .alias(DELIMITER.join([col, _LAG_COLUMN, str(lag)]))
                        for col in all_expected_cols
                        if col
                        not in {dt_column, _ROW_IDX_COLUMN, _COLUMN_PREFIX_COLUMN}
                    ]
                )
            # Find all the prefixes used for the identifier
            prefixes = (
                id_df.select(_COLUMN_PREFIX_COLUMN).unique().to_series().to_list()
            )
            for prefix in prefixes:
                # Merge the prefixes back into the main dataframe
                prefix_df = id_df.filter(pl.col(_COLUMN_PREFIX_COLUMN) == prefix)
                col_map = {
                    x: prefix + x
                    for x in prefix_df.columns
                    if x not in {dt_column, _COLUMN_PREFIX_COLUMN, _ROW_IDX_COLUMN}
                }
                prefix_df = prefix_df.drop([_COLUMN_PREFIX_COLUMN, dt_column]).rename(
                    col_map
                )
                pl_df = pl_df.join(prefix_df, on=_ROW_IDX_COLUMN, how="left")
                pl_df = pl_df.with_columns(
                    [
                        pl.coalesce([pl.col(f"{col}_right"), pl.col(col)]).alias(col)
                        for col in prefix_df.columns
                        if col in pl_df.columns and col + "_right" in pl_df.columns
                    ]
                )
                pl_df = pl_df.drop([x for x in pl_df.columns if x.endswith("_right")])

    return pl_df.drop(_ROW_IDX_COLUMN).to_pandas()
