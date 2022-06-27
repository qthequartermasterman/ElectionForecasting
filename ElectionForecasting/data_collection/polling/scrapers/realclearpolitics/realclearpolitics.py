from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from rcp import get_polls, get_poll_data
from ElectionForecasting.data_collection.DataCollectionUtils import str_to_date

from ..AbstractScraper import AbstractScraper

generic_ballot_url = 'https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html'

ELECTION_DATE = str_to_date('11/8/22')


# polls = get_polls(candidate="Biden")[0]
# data = get_poll_data(polls['url'], csv_output=True)

def split_date(date_interval_string: str) -> (datetime, datetime):
    start, end = date_interval_string.split(' - ')
    start, end = start + '/22', end + '/22'
    start, end = str_to_date(start), str_to_date(end)
    return pd.Series([start, end])


def split_sample_type(sample_size_type: str):
    if sample_size_type == '--':
        return pd.Series([0, sample_size_type])
    try:
        sample_size, sample_type = sample_size_type.split(maxsplit=1)
    except ValueError:  # trying to unpack the split if there is only one item will throw a ValueError
        return pd.Series([0, sample_size_type])
    return pd.Series([int(sample_size), sample_type])



class RealClearPoliticsScraper(AbstractScraper):
    _registry_name = 'realclearpolitics'

    @classmethod
    def get_raw_generic_ballot_data(cls, url: Optional[str] = None) -> pd.DataFrame:
        data = get_poll_data(url or generic_ballot_url, csv_output=True)

        raw = pd.DataFrame(data[1:], columns=data[0]).rename(columns={'Poll': 'pollster',
                                                                      'Republicans (R)': 'Republican',
                                                                      'Democrats (D)': 'Democratic',
                                                                      })
        raw['District'] = 'Generic Ballot'
        raw[['StartDate', 'EndDate']] = raw['Date'].apply(split_date)
        raw[[AbstractScraper.sample_size_col, AbstractScraper.population_col]] = raw['Sample'].apply(split_sample_type)
        raw[AbstractScraper.sample_size_col] = raw[AbstractScraper.sample_size_col].astype(int)
        raw['ElectionDate'] = ELECTION_DATE
        raw['Libertarian'] = 0
        raw['Green'] = 0
        raw['Independent'] = 0
        return raw

    @classmethod
    def get_raw_house_data(cls, url: Optional[str] = None) -> pd.DataFrame:
        pass


if __name__ == '__main__':
    scraper = RealClearPoliticsScraper()
    raw_generic = scraper.get_raw_generic_ballot_data()
