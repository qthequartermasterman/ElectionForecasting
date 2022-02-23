from functools import wraps
import pandas as pd
import os
import time


def cache_download_csv_to_file(filename, refresh_time=None):
    """
    Save a pandas DataFrame to a csv file for faster caching.
    :param filename: filepath to save the cached csv
    :param refresh_time: Time in hours. If the file has not been updated in longer than refresh_time, generate the
        file anew. If refresh_time=None, the file will never be regenerated if a cached version exists.
    :return:
    """

    def cache_wrapper(func):
        @wraps(func)
        def inside_wrapper(*args, **kwargs):
            # TODO: Refresh the file if it has been longer than refresh_time

            try:
                if refresh_time is not None and os.path.getmtime(filename) + int(refresh_time * 60 * 60) < time.time():
                    print('File is too old')
                    raise FileNotFoundError(f'{filename} is too old and needs to be refreshed')
                dataframe: pd.DataFrame = pd.read_csv(filename, index_col=0)
            except FileNotFoundError:
                dataframe = func(*args, **kwargs)
                dataframe.to_csv(filename)
            return dataframe

        return inside_wrapper

    return cache_wrapper
