"""Calculate bet features."""

import datetime
import functools

import pandas as pd
from sklearn.metrics import mean_squared_error  # type: ignore
from tqdm import tqdm

from .columns import DELIMITER
from .identifier import Identifier


def _force_utc_aware(series, timezone="UTC"):
    series = pd.to_datetime(series, errors="coerce")

    if series.dt.tz is None:
        return series.dt.tz_localize(timezone, ambiguous="NaT", nonexistent="NaT")
    return series.dt.tz_convert(timezone)


def bet_process(
    df: pd.DataFrame, identifiers: list[Identifier], dt_column: str
) -> pd.DataFrame:
    """Process bets."""
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    tqdm.pandas(desc="Bets Features")
    bookie_odds: list[float] = []
    wins: list[float] = []

    def apply_bets(
        row: pd.Series, identifiers: list[Identifier], dt_column: str
    ) -> pd.Series:
        nonlocal bookie_odds
        nonlocal wins

        try:
            game_dt = pd.Timestamp(row[dt_column]).tz_localize("UTC")
        except TypeError:
            game_dt = pd.Timestamp(row[dt_column]).tz_convert("UTC")

        price_efficiency = (
            None if not bookie_odds else mean_squared_error(bookie_odds, wins)
        )
        local_bookie_odds = []
        local_points = []
        for identifier in identifiers:
            if identifier.points_column is None:
                continue
            if identifier.points_column not in row:
                continue

            odds_data = []
            bookies_data = []
            dts_data = []
            for bet in identifier.bets:
                if bet.odds_column not in row or bet.bookie_id_column not in row:
                    continue
                odds = row[bet.odds_column]
                if pd.isnull(odds):
                    continue
                bookie_id = row[bet.bookie_id_column]
                if pd.isnull(bookie_id):
                    continue
                if bet.dt_column is None or bet.dt_column not in row:
                    dt = game_dt - datetime.timedelta(hours=1)
                else:
                    dt = row[bet.dt_column]
                    if pd.isnull(dt):
                        dt = game_dt - datetime.timedelta(hours=1)
                odds_data.append(odds)
                bookies_data.append(bookie_id)
                dts_data.append(dt)
            df = pd.DataFrame(
                data={
                    "odds": odds_data,
                    "bookie": bookies_data,
                    "dt": dts_data,
                }
            )
            if df.empty:
                continue
            df["dt"] = _force_utc_aware(df["dt"])
            df = df.sort_values(by="dt")
            odds_max = df["odds"].max()
            odds_min = df["odds"].min()
            earliest_odds = df["odds"].iloc[0]
            latest_odds = df["odds"].iloc[-1]
            earliest_dt = df["dt"].iloc[0]
            latest_dt = df["dt"].iloc[-1]

            direction_changes = 0
            big_shifts = 0
            consensus_flips = 0
            resampled_df = pd.DataFrame()
            for bookie in df["bookie"].unique():
                bookie_df = df[df["bookie"] == bookie]
                bookies_odds = bookie_df["odds"].to_list()
                current_odds = None
                current_direction = None
                for odd in bookies_odds:
                    if current_odds is None:
                        current_odds = odd
                        continue
                    if current_direction is None:
                        current_direction = 1 if odd >= current_odds else -1
                        current_odds = odd
                        continue
                    new_direction = 1 if odd >= current_odds else -1
                    if new_direction != current_direction:
                        direction_changes += 1
                    if max(current_odds, odd) / min(current_odds, odd) > 1.1:
                        big_shifts += 1
                    if min(current_odds, odd) < 2.0 < max(current_odds, odd):
                        consensus_flips += 1
                    current_odds = odd
                    current_direction = new_direction
                resampled_df = pd.concat(
                    [
                        resampled_df,
                        pd.DataFrame(
                            data={
                                bookie + "_odds": bookies_odds,
                            },
                            index=bookie_df["dt"],
                        ),
                    ]
                )
            resampled_df = resampled_df.resample("5T").last()
            resampled_df = resampled_df.ffill()

            ffill_df = df.set_index("dt").ffill()
            oneday_df = ffill_df[ffill_df.index > game_dt - datetime.timedelta(days=1)]
            final_odds = resampled_df.mean(axis=1).to_list()[-1]

            row[DELIMITER.join([identifier.column_prefix, "odds", "max"])] = odds_max
            row[DELIMITER.join([identifier.column_prefix, "odds", "min"])] = odds_min
            row[DELIMITER.join([identifier.column_prefix, "odds", "mean"])] = df[
                "odds"
            ].mean()
            row[DELIMITER.join([identifier.column_prefix, "odds", "median"])] = df[
                "odds"
            ].median()
            row[DELIMITER.join([identifier.column_prefix, "odds", "spread"])] = (
                odds_max - odds_min
            )
            row[DELIMITER.join([identifier.column_prefix, "odds", "bookies"])] = df[
                "bookie"
            ].nunique()
            row[DELIMITER.join([identifier.column_prefix, "odds", "roc"])] = (
                latest_odds - earliest_odds
            ) / (latest_dt - earliest_dt).total_seconds()
            row[DELIMITER.join([identifier.column_prefix, "odds", "mom"])] = (
                latest_odds - earliest_odds
            )
            row[DELIMITER.join([identifier.column_prefix, "odds", "directchanges"])] = (
                direction_changes
            )
            row[DELIMITER.join([identifier.column_prefix, "odds", "samples"])] = len(df)
            # row[DELIMITER.join([identifier.column_prefix, "odds", "ewm"])] = (
            #    resampled_df.mean(axis=1).ewm(alpha=0.2, adjust=False).mean()
            # )
            row[DELIMITER.join([identifier.column_prefix, "odds", "bigshifts"])] = (
                big_shifts
            )
            row[
                DELIMITER.join([identifier.column_prefix, "odds", "consensusflips"])
            ] = consensus_flips
            if len(oneday_df) > 1:
                row[DELIMITER.join([identifier.column_prefix, "odds", "roc1day"])] = (
                    oneday_df["odds"].iloc[-1] - oneday_df["odds"].iloc[0]
                ) / datetime.timedelta(days=1).total_seconds()
            else:
                row[DELIMITER.join([identifier.column_prefix, "odds", "roc1day"])] = 0.0
            row[DELIMITER.join([identifier.column_prefix, "odds"])] = final_odds
            row[
                DELIMITER.join([identifier.column_prefix, "odds", "priceefficiency"])
            ] = price_efficiency
            local_bookie_odds.append(1.0 / final_odds)

            points = row[identifier.points_column]
            if pd.isnull(points):
                continue
            local_points.append(points)

        if local_points:
            bookie_odds.extend(local_bookie_odds)
            wins.extend([float(x == max(local_points)) for x in local_points])

        return row

    return df.progress_apply(
        functools.partial(
            apply_bets,
            identifiers=identifiers,
            dt_column=dt_column,
        ),
        axis=1,
    ).copy()  # type: ignore
