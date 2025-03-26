import sys

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


class CustomStdout:
    def __init__(self, custom_log_func):
        self.custom_log_func = custom_log_func  # Your logging function
        self.buffer = []  # Buffer to handle partial lines

    def write(self, text: str):
        # Split text into lines and send completed lines to the custom function
        if text == '\n':  # Handle standalone newlines
            self.buffer.append('')
        parts = text.split('\n')
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                # Complete line found
                self.buffer.append(part)
                full_line = '\n'.join(self.buffer)
                self.custom_log_func(full_line)
                self.buffer = []
            else:
                # Partial line remains
                self.buffer.append(part)

    def flush(self):
        # Optional: Send remaining buffer content if needed
        if self.buffer:
            self.custom_log_func('\n'.join(self.buffer))
            self.buffer = []
        sys.__stdout__.flush()  # Preserve default flush behavior


from contextlib import contextmanager


@contextmanager
def redirect_stdout_to_logger(custom_log_func):
    original_stdout = sys.stdout
    sys.stdout = CustomStdout(custom_log_func)
    try:
        yield
    finally:
        sys.stdout = original_stdout  # Restore original stdout

