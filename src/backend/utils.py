import pandas as pd
import os
from typing import Union, Any
import io


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

    # Case 2: X is a string (could be a file path or plain text)
    elif isinstance(X, str):
        if os.path.isfile(X):
            # It's a file path
            _, ext = os.path.splitext(X)
            ext = ext.lower()
            if ext == '.txt':
                try:
                    with open(X, 'r', encoding='utf-8') as file:
                        content = file.read()
                    df = pd.DataFrame({'text': [content]})
                    return df
                except Exception as e:
                    raise TypeError(f"Error reading text file '{X}': {e}")
            elif ext == '.csv':
                try:
                    df = pd.read_csv(X)
                    return df
                except Exception as e:
                    raise TypeError(f"Error reading CSV file '{X}': {e}")
            else:
                raise TypeError(f"Unsupported file extension '{ext}'. Only .txt and .csv are supported.")
        else:
            # It's a plain string
            df = pd.DataFrame({'text': [X]})
            return df

    # Case 3: X is a stream (has a read() method)
    elif hasattr(X, 'read') and callable(X.read):
        try:
            # Attempt to read as text
            content = X.read()
            if isinstance(content, bytes):
                # If bytes, decode using utf-8
                content = content.decode('utf-8')
            df = pd.DataFrame({'text': [content]})
            return df
        except Exception as e:
            raise TypeError(f"Error reading from stream: {e}")

    else:
        raise TypeError(
            "Unsupported type for parsing. Supported types are: pandas.DataFrame, str (filepath or text), and stream objects.")

