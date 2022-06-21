from collections import defaultdict
from typing import Optional
from datetime import date
import pandas as pd

import urls

from ElectionForecasting.data_collection.DataCollectionUtils import cache_download_csv_to_file

REFRESH_RATE = 0  # 12  # Refresh this every 12 hr


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


def str_to_date(date_str: str) -> date:
    m, d, y = date_str.split('/')
    m, d, y = int(m), int(d), 2000 + int(y)
    print(m, d, y)
    return date(y, m, d)


def get_raw_poll_data(url: Optional[str] = None) -> pd.DataFrame:
    poll_url = url
    poll_csv = pd.read_csv(poll_url, index_col='poll_id')
    poll_csv['District'] = poll_csv['state'].astype(str) + '-' + poll_csv['seat_number'].astype(str).str.pad(2,
                                                                                                             fillchar='0')
    poll_csv['party'] = poll_csv['party'].apply(rename_party)
    poll_csv['end_date'] = poll_csv['end_date'].apply(str_to_date)
    poll_csv['election_date'] = poll_csv['election_date'].apply(str_to_date)
    return poll_csv


def get_raw_generic_ballot_poll_data(url: Optional[str] = None) -> pd.DataFrame:
    poll_url = url
    poll_csv = pd.read_csv(poll_url, index_col='poll_id')
    poll_csv['District'] = 'Generic Ballot'
    poll_csv['end_date'] = poll_csv['end_date'].apply(str_to_date)
    poll_csv['election_date'] = poll_csv['election_date'].apply(str_to_date)
    poll_csv = poll_csv.rename(columns={'rep': 'Republican', 'dem': 'Democratic', 'ind': 'Independent'})
    poll_csv['pct'] = poll_csv['Republican']
    poll_csv['party'] = 'Republican'
    return poll_csv


def compile_raw_polls_to_timeseries(raw_poll_df: pd.DataFrame, party: str, election_date: date) -> pd.DataFrame:
    compiled_df: pd.DataFrame = pd.DataFrame()
    # Take each row, and put the poll results in the correct date column and district row

    district_date_counts = defaultdict(lambda: 0)
    for index, row in raw_poll_df.iterrows():
        # print(row['election_date'], row['party'])
        if row['election_date'] == election_date and row['party'] == party:
            # TODO: Logic about what to do if multiple polls for a district occur on the same date
            # TODO: For now, just take the average
            if row['District'] in compiled_df.index and row['end_date'] in compiled_df.columns:
                compiled_df.loc[row['District'], row['end_date']] += row['pct']
            else:
                compiled_df.loc[row['District'], row['end_date']] = row['pct']
            district_date_counts[(row['District'], row['end_date'])] += 1
    compiled_df = compiled_df.copy()  # Defragment the frame
    for (district, date), count in district_date_counts.items():
        compiled_df.loc[district, date] /= count
    compiled_df = compiled_df.sort_index()
    compiled_df = compiled_df.sort_index(axis=1, ascending=True)
    return compiled_df


@cache_download_csv_to_file('data/fivethirtyeight/house_raw.csv', refresh_time=REFRESH_RATE)
def get_raw_house_data(url: Optional[str] = None) -> pd.DataFrame:
    return get_raw_poll_data(url or urls.house_polls)


@cache_download_csv_to_file('data/fivethirtyeight/house_raw_poll_timeseries.csv', refresh_time=REFRESH_RATE)
def compile_raw_house_data_to_timeseries(raw_poll_df: pd.DataFrame, party: str, election_date: date) -> pd.DataFrame:
    return compile_raw_polls_to_timeseries(raw_poll_df, party, election_date)


@cache_download_csv_to_file('data/fivethirtyeight/generic_ballot_raw.csv', refresh_time=REFRESH_RATE)
def get_raw_generic_ballot_data(url: Optional[str] = None) -> pd.DataFrame:
    return get_raw_generic_ballot_poll_data(url or urls.generic_ballot_polls)


@cache_download_csv_to_file('data/fivethirtyeight/generic_ballot_raw_poll_timeseries.csv', refresh_time=REFRESH_RATE)
def compile_raw_generic_ballot_data_to_timeseries(raw_poll_df: pd.DataFrame, party: str,
                                                  election_date: date) -> pd.DataFrame:
    return compile_raw_polls_to_timeseries(raw_poll_df, party, election_date)


raw = get_raw_house_data()
raw_generic = get_raw_generic_ballot_data()

election_date = str_to_date('11/8/22')
compiled = compile_raw_house_data_to_timeseries(raw, 'Republican', election_date)
compiled_generic = compile_raw_generic_ballot_data_to_timeseries(raw_generic, 'Republican', election_date)
