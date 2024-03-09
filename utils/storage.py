import pandas as pd
import os

def save_to_parquet(df, filename):
    df.to_parquet(filename, index=False)

def load_parquet(filename):
    """Load a Parquet file into a DataFrame."""
    if os.path.exists(filename):
        return pd.read_parquet(filename)
    else:
        return pd.DataFrame()