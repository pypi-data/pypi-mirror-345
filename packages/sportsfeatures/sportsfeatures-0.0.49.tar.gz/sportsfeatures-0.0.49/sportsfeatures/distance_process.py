"""Process the distance between two locations."""

# pylint: disable=duplicate-code,too-many-branches

import functools

import geopy.distance  # type: ignore
import pandas as pd
from tqdm import tqdm

from .columns import DELIMITER
from .entity_type import EntityType
from .identifier import Identifier


def distance_process(df: pd.DataFrame, identifiers: list[Identifier]) -> pd.DataFrame:
    """Process a dataframe for offensive efficiency."""
    tqdm.pandas(desc="Distance Features")
    last_identifier_locations: dict[str, tuple[float, float]] = {}
    team_identifiers = [x for x in identifiers if x.entity_type == EntityType.TEAM]
    player_identifiers = [x for x in identifiers if x.entity_type == EntityType.PLAYER]
    venue_identifiers = [x for x in identifiers if x.entity_type == EntityType.VENUE]

    def record_distance(
        row: pd.Series,
        team_identifiers: list[Identifier],
        player_identifiers: list[Identifier],
        venue_identifiers: list[Identifier],
    ) -> pd.Series:
        nonlocal identifiers
        nonlocal last_identifier_locations

        current_location = None
        for venue_identifier in venue_identifiers:
            if venue_identifier.latitude_column is None:
                continue
            if venue_identifier.latitude_column not in row:
                continue
            latitude = row[venue_identifier.latitude_column]
            if pd.isnull(latitude):
                continue
            if venue_identifier.longitude_column is None:
                continue
            if venue_identifier.longitude_column not in row:
                continue
            longitude = row[venue_identifier.longitude_column]
            if pd.isnull(longitude):
                continue
            current_location = (latitude, longitude)
        if current_location is None:
            return row

        for identifier in team_identifiers + player_identifiers:
            if identifier.column not in row:
                continue
            identifier_id = row[identifier.column]
            if pd.isnull(identifier_id):
                continue
            if not isinstance(identifier_id, str):
                continue
            key = "_".join([str(identifier.entity_type), identifier_id])
            last_location = last_identifier_locations.get(key)
            if last_location is not None:
                row[DELIMITER.join([identifier.column_prefix, "latitudediff"])] = abs(
                    last_location[0] - current_location[0]
                )
                row[DELIMITER.join([identifier.column_prefix, "longitudediff"])] = abs(
                    last_location[1] - current_location[1]
                )
                row[DELIMITER.join([identifier.column_prefix, "distance"])] = (
                    geopy.distance.geodesic(last_location, current_location).km
                )
            last_identifier_locations[key] = current_location

        return row

    return df.progress_apply(
        functools.partial(
            record_distance,
            team_identifiers=team_identifiers,
            player_identifiers=player_identifiers,
            venue_identifiers=venue_identifiers,
        ),
        axis=1,
    ).copy()  # type: ignore
