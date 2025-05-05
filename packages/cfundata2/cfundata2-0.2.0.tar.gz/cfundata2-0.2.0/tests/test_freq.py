import pandas as pd

from cfundata2 import FREQUENCY2_PATH, FREQUENCY_PATH


def test_frequency():
    # Read the parquet file
    print(FREQUENCY2_PATH)
    print(type(FREQUENCY2_PATH))
    df = pd.read_parquet(FREQUENCY_PATH)
    print(df.head())
    print(df.columns)
    print(df.dtypes)
    print(df.info())
