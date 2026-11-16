import pandas as pd
def preprocess_data(df):

    df = df.drop_duplicates().copy()

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")


    categorical_columns = [
        "road_type", "weather", "main_cause"
    ]

    for col in categorical_columns:
        df[col] = df[col].fillna("Unknown")

    
    df["casualties"] = pd.to_numeric(
        df["casualties"], errors="coerce"
    )

    df["casualties"] = df["casualties"].fillna(
        df["casualties"].median()
    )

    return df
