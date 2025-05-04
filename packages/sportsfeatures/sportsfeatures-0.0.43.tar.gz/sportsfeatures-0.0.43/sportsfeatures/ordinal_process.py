"""Process a dataframe for its ordinal information."""

import pandas as pd
from feature_engine.encoding import OrdinalEncoder


def ordinal_process(df: pd.DataFrame, categorical_features: set[str]) -> pd.DataFrame:
    """Process ordinal features."""
    od = OrdinalEncoder(missing_values="ignore", encoding_method="arbitrary")
    df = od.fit_transform(df)
    for categorical_feature in categorical_features:
        if categorical_feature not in df.columns.values:
            continue
        df[categorical_feature] = (
            df[categorical_feature].fillna(0).astype(int).astype("category")
        )
    return df.copy()
