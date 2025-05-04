"""Process a dataframe for its ordinal information."""

import pandas as pd
from feature_engine.encoding import OrdinalEncoder


def ordinal_process(df: pd.DataFrame, categorical_features: set[str]) -> pd.DataFrame:
    """Process ordinal features."""
    if not categorical_features:
        return df
    od = OrdinalEncoder(
        missing_values="ignore",
        encoding_method="arbitrary",
        variables=list(categorical_features),
    )
    df = od.fit_transform(df)
    for categorical_feature in categorical_features:
        if categorical_feature not in df.columns.values:
            continue
        try:
            df[categorical_feature] = (
                df[categorical_feature].fillna(0).astype(int).astype("category")
            )
        except TypeError:
            pass
    return df.copy()
