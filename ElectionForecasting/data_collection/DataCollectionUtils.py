from functools import wraps
import pandas as pd


def cache_download_csv_to_file(filename):
    def cache_wrapper(func):
        @wraps(func)
        def inside_wrapper(*args, **kwargs):
            try:
                dataframe: pd.DataFrame = pd.read_csv(filename, index_col=0)
            except FileNotFoundError:
                dataframe = func(*args, **kwargs)
                dataframe.to_csv(filename)
            return dataframe

        return inside_wrapper

    return cache_wrapper
