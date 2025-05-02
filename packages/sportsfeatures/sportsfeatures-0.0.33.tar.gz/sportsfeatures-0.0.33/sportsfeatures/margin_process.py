"""Calculate margin features."""

# pylint: disable=too-many-branches

import pandas as pd
from tqdm import tqdm

from .columns import DELIMITER
from .identifier import Identifier


def margin_process(df: pd.DataFrame, identifiers: list[Identifier]) -> pd.DataFrame:
    """Process margins between teams."""
    tqdm.pandas(desc="Margins Features")
    identifiers_ts: dict[str, dict[str, float]] = {}

    def record_margin(row: pd.Series) -> pd.Series:
        nonlocal identifiers
        nonlocal identifiers_ts

        entity_dicts: dict[str, dict[str, dict[str, float]]] = {}

        for identifier in identifiers:
            if identifier.column not in row:
                continue
            identifier_id = row[identifier.column]
            if pd.isnull(identifier_id):
                continue
            entity_dict = entity_dicts.get(str(identifier.entity_type), {})
            identifier_dict = entity_dict.get(identifier_id, {})
            columns = {
                x[len(identifier.column_prefix) :] for x in identifier.feature_columns
            }
            if identifier.points_column is not None:
                columns.add(identifier.points_column[len(identifier.column_prefix) :])

            for column in columns:
                full_column = identifier.column_prefix + column
                if full_column not in row:
                    continue
                value = row[full_column]
                try:
                    identifier_dict[column] = float(value)
                except TypeError:
                    pass

            entity_dict[identifier_id] = identifier_dict
            entity_dicts[str(identifier.entity_type)] = entity_dict

        for entity_dict in entity_dicts.values():
            max_dict: dict[str, float] = {}
            for identifier_dict in entity_dict.values():
                for column, value in identifier_dict.items():
                    max_dict[column] = max(max_dict.get(column, 0.0), value)
            for identifier_id, identifier_dict in entity_dict.items():
                for identifier in identifiers:
                    if identifier.column not in row:
                        continue
                    identifier_id_check = row[identifier.column]
                    if pd.isnull(identifier_id_check):
                        continue
                    if identifier_id_check != identifier_id:
                        continue
                    identifier_ts_cols: dict[str, float] = identifiers_ts.get(
                        identifier_id, {}
                    )
                    # Copy the old columns in
                    for column, value in identifier_ts_cols.items():
                        full_column = identifier.column_prefix + column
                        row[full_column] = value
                    identifier_ts_cols = {}
                    # Create the new columns
                    for column, value in identifier_dict.items():
                        margin_absolute_column = DELIMITER.join(
                            [column, "margin", "absolute"]
                        )
                        identifier_ts_cols[margin_absolute_column] = (
                            value - max_dict[column]
                        )
                        margin_relative_column = DELIMITER.join(
                            [column, "margin", "relative"]
                        )
                        identifier_ts_cols[margin_relative_column] = (
                            0.0
                            if max_dict[column] == 0.0
                            else (value / max_dict[column])
                        )
                    identifiers_ts[identifier_id] = identifier_ts_cols
                    break

        return row

    return df.progress_apply(record_margin, axis=1)  # type: ignore
