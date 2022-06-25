from collections import defaultdict
from typing import Optional
from datetime import date, timedelta
import pandas as pd

try:
    from . import urls
except ImportError:
    import urls

from ElectionForecasting.data_collection.DataCollectionUtils import cache_download_csv_to_file, str_to_date
from ElectionForecasting.data_collection.scrapers.AbstractScraper import AbstractScraper

REFRESH_RATE = 0  # 12  # Refresh this every 12 hr


class FiveThirtyEightScraper(AbstractScraper):
    _registry_name = 'fivethirtyeight'

    @staticmethod
    def get_raw_poll_data(url: Optional[str] = None) -> pd.DataFrame:
        district_col = FiveThirtyEightScraper.district_col
        party_col = FiveThirtyEightScraper.party_col
        end_date_col = FiveThirtyEightScraper.end_date_col
        election_date_col = FiveThirtyEightScraper.election_date_col
        percent_col = FiveThirtyEightScraper.percent_col
        start_date_col = FiveThirtyEightScraper.start_date_col

        poll_url = url
        poll_csv = pd.read_csv(poll_url, index_col='poll_id')
        poll_csv[district_col] = poll_csv['state'].astype(str) + '-' + poll_csv['seat_number'].astype(str).str.pad(2,
                                                                                                                   fillchar='0')
        poll_csv[party_col] = poll_csv['party'].apply(rename_party)
        poll_csv[end_date_col] = poll_csv['end_date'].apply(str_to_date)
        poll_csv[election_date_col] = poll_csv['election_date'].apply(str_to_date)
        poll_csv = poll_csv.rename(columns={'start_date': start_date_col,
                                            'end_date':end_date_col,
                                            'pct': percent_col})
        return poll_csv

    @staticmethod
    def get_raw_generic_ballot_poll_data(url: Optional[str] = None) -> pd.DataFrame:
        district_col = FiveThirtyEightScraper.district_col
        party_col = FiveThirtyEightScraper.party_col
        end_date_col = FiveThirtyEightScraper.end_date_col
        election_date_col = FiveThirtyEightScraper.election_date_col
        percent_col = FiveThirtyEightScraper.percent_col
        start_date_col = FiveThirtyEightScraper.start_date_col

        poll_csv = pd.read_csv(url, index_col='poll_id')
        poll_csv[district_col] = 'Generic Ballot'
        poll_csv[end_date_col] = poll_csv['end_date'].apply(str_to_date)
        poll_csv[election_date_col] = poll_csv['election_date'].apply(str_to_date)
        poll_csv = poll_csv.rename(columns={'rep': 'Republican',
                                            'dem': 'Democratic',
                                            'ind': 'Independent',
                                            'start_date': start_date_col,
                                            'end_date':end_date_col,
                                            'pct': percent_col
                                            })
        poll_csv[percent_col] = poll_csv['Republican']
        poll_csv[party_col] = 'Republican'
        poll_csv['Libertarian'] = 0
        poll_csv['Green'] = 0
        return poll_csv

    @classmethod
    @cache_download_csv_to_file('../../data/fivethirtyeight/generic_ballot_raw.csv', refresh_time=REFRESH_RATE)
    def get_raw_generic_ballot_data(cls, url: Optional[str] = None) -> pd.DataFrame:
        return cls.get_raw_generic_ballot_poll_data(url or urls.generic_ballot_polls)

    @classmethod
    @cache_download_csv_to_file('../../data/fivethirtyeight/house_raw_poll_timeseries.csv', refresh_time=REFRESH_RATE)
    def compile_raw_house_data_to_timeseries(cls, raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                             starting_date: Optional[date] = None) -> pd.DataFrame:
        return AbstractScraper.compile_raw_house_data_to_timeseries(raw_poll_df, party, election_date, starting_date)

    @classmethod
    @cache_download_csv_to_file('../../data/fivethirtyeight/generic_ballot_raw_poll_timeseries.csv',
                                refresh_time=REFRESH_RATE)
    def compile_raw_generic_ballot_data_to_timeseries(cls, raw_poll_df: pd.DataFrame, party: str, election_date: date,
                                                      starting_date: Optional[date] = None) -> pd.DataFrame:
        return AbstractScraper.compile_raw_generic_ballot_data_to_timeseries(raw_poll_df, party, election_date,
                                                                             starting_date)

    @classmethod
    @cache_download_csv_to_file('../../data/fivethirtyeight/house_raw.csv', refresh_time=REFRESH_RATE)
    def get_raw_house_data(cls, url: Optional[str] = None) -> pd.DataFrame:
        return cls.get_raw_poll_data(url or urls.house_polls)


def rename_party(party: str) -> str:
    """
    Take fivethirtyeight house party labels and replace them with our standard names
    :param party:
    :return:
    """
    if party.upper() == 'REP':
        return 'Republican'
    if party.upper() == 'DEM':
        return 'Democratic'
    if party.upper() == 'LIB':
        return 'Libertarian'
    if party.upper() == 'GRN':
        return 'Green'
    return 'Independent'


if __name__ == '__main__':
    num_days_polls = 240  # We will track the polls starting 80 days in advance
    scraper = FiveThirtyEightScraper()
    raw = scraper.get_raw_house_data()
    raw_generic = scraper.get_raw_generic_ballot_data()
    election_date = str_to_date('11/8/22')
    polls_start_date = election_date - timedelta(days=num_days_polls)

    compiled = scraper.compile_raw_house_data_to_timeseries(raw, 'Republican', election_date, polls_start_date)
    compiled_generic = scraper.compile_raw_generic_ballot_data_to_timeseries(raw_generic, 'Republican', election_date,
                                                                             polls_start_date)
