import pandas as pd
import os
from typing import Union, Any

from io import StringIO


def parseWildcardToDataframe(X: Any) -> pd.DataFrame:
    """
    Parses the input X and returns a pandas DataFrame based on the following rules:

    - If X is already a pandas DataFrame, return it unchanged.
    - If X is a file path:
        - If it's a .txt file, create a DataFrame with one column "text" and one row containing the file's content.
        - If it's a .csv file, read it into a DataFrame using pandas.
    - If X is a string, treat it as text and create a DataFrame with one column "text" and one row containing the string.
    - If X is a stream (has a read() method), read its content and treat it as text, creating a DataFrame with one column "text".

    Args:
        X: The input to parse. Can be a pandas DataFrame, file path (str), string, or stream.

    Returns:
        pd.DataFrame: The resulting DataFrame based on the input.

    Raises:
        TypeError: If X is not a supported type or if a file path does not exist.
    """
    # Case 1: X is already a pandas DataFrame
    if isinstance(X, pd.DataFrame):
        return X

    # Case 2: X is a csv file
    elif isinstance(X, str):
        csv_data = StringIO(X)
        return pd.read_csv(csv_data)


    else:
        raise TypeError(
            "Unsupported type for parsing. Supported types are: pandas.DataFrame, str (filepath or text), and stream objects.")

