from typing import Optional

import pandas as pd

import urls

from ElectionForecasting.data_collection.DataCollectionUtils import cache_download_csv_to_file


@cache_download_csv_to_file('data/fivethirtyeight/house.csv')
def get_raw_house_data(url: Optional[str] = None):
    house_url = url or urls.house_polls
    house_csv = pd.read_csv(house_url, index_col='poll_id')
    house_csv['District'] = house_csv['state'] + house_csv['seat_number'].astype(str)
    return house_csv

get_raw_house_data()