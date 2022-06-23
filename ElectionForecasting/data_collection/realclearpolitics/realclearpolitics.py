from datetime import datetime
from typing import Optional

import pandas as pd
from rcp import get_polls, get_poll_data
from ElectionForecasting.data_collection.DataCollectionUtils import str_to_date

generic_ballot_url = 'https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html'

# polls = get_polls(candidate="Biden")[0]
# data = get_poll_data(polls['url'], csv_output=True)

def split_date(date_interval_string:str)->(datetime,datetime):
    start,end = date_interval_string.split(' - ')
    start,end = start + '/22', end+'/22'
    start,end = str_to_date(start), str_to_date(end)
    return pd.Series([start,end])



def get_raw_generic_ballot_poll_data(url: Optional[str] = None) -> pd.DataFrame:
    data = get_poll_data(url or generic_ballot_url, csv_output=True)

    raw = pd.DataFrame(data[1:], columns=data[0]).rename(columns={'Poll': 'pollster',
                                                                  'Republicans (R)': 'Republican',
                                                                  'Democrats (D)': 'Democratic',
                                                                  })
    raw['District'] = 'Generic Ballot'
    raw['pct'] = raw['Republican']
    raw['party'] = 'Republican'
    raw[['start_date', 'end_date']] = raw['Date'].apply(split_date)
    return raw


