import math
import re
from typing import List, Tuple, Dict, Union, Callable, Optional

from wikitablescrape.parse import Parser
import requests
from io import StringIO
import pandas as pd

from DataCollectionUtils import cache_download_csv_to_file


def right_replace(s: str, old: str, new: str, count: int = 1):
    """
    Replace instances of `old` with `new` iterating over `s` from the right. Max `count` times.
    :param s: string over which to replace `old`
    :param old: string to replace
    :param new: string to replace `old` with
    :param count: maximum number of times to replace `old`
    :return: `s` with at most `count` instances of `old` replaced with `new`, starting from the right
    """
    return new.join(s.rsplit(old, count))


def rename_congressional_district(name: str) -> str:
    if 'Note' in name:
        return ''
    if 'Special' in name:
        name = name.rsplit('Special')[0]
        name = name.strip()
    state, num = name.rsplit(' ', maxsplit=1)
    if 'at-large' in num:
        num = '00'
    if len(num) == 1:
        num = '0' + num
    return state + '-' + num


def handle_first_elected(first_elected):
    if isinstance(first_elected, int):
        return first_elected
    if isinstance(first_elected, str):
        if 'None' in first_elected or 'Vacant' in first_elected or 'New seat' in first_elected or 'Open' in first_elected:
            return -1
        try:
            first_elected = first_elected.replace('/', ' ')
            numbers = [s for s in first_elected.split() if s.isdigit()]
            if numbers:
                return int(numbers[0])
            else:
                return -1
        except ValueError:
            return -1


def extract_election_data(text: str) -> Dict[str, Union[str, float]]:
    """

    :param text:
    :return:
    """
    list_of_results = {}
    if text[:2] == 'Y ':
        text = text[2:]
    for character in '<>{}':
        text = text.replace(character, '')
    if 'round' in text:
        # Instant run-off voting was used. For now ignore the second round.
        # TODO: Capture Instant Run-off results
        text = re.sub(r'\(([0-9.]+%) round 1, [0-9.]+% round 2\)', r'\1', text)
        text = re.sub(r'\(([0-9.]+%) round 1\)', r'\1', text)
    if '%)' in text:
        # Also a run-off, but we only want the second round.
        text = re.sub(r'[0-9.]+% \(([0-9.]+%)\)', r'\1', text)
    candidates = text.split('% ')
    for candidate in candidates:
        if not candidate:
            continue
        if 'Unopposed' in candidate:
            continue
        if candidate[-1] == '%':
            candidate = candidate[:-1]
        temporary_separator = '--&--'  # This is a token we'll use to make it easier to split the string
        candidate = right_replace(candidate, "(", temporary_separator)
        candidate = right_replace(candidate, ")", temporary_separator)
        try:
            name, party, percent = candidate.split(temporary_separator)
        except ValueError:
            # Not enough values to unpack (party missing)
            name, percent = candidate.rsplit(' ', maxsplit=1)
            party = ''

        try:
            name, party, percent = name.strip(), party.strip(), float(percent)
        except ValueError:
            # float failed, meaning that percent is missing
            name, party, percent = name.strip(), party.strip(), math.nan
        if party in ('Republican', 'Democratic', 'Green', 'Libertarian'):
            if party not in list_of_results.keys() or percent > list_of_results[party]:
                list_of_results[party] = percent
                list_of_results[party + ' candidate'] = name
    return list_of_results


def extract_election_data_series(district_row: pd.Series) -> pd.Series:
    try:
        result_tuples = extract_election_data(district_row['Candidates'])
    except TypeError:
        result_tuples = extract_election_data('% ')
    return pd.Series(result_tuples)


def download_district_results(url, start=None, stop=None) -> pd.DataFrame:
    resp = requests.get(url)
    parser = Parser(resp.text)

    pandas_tables_by_state = []

    def header_row_bool(url, tag=''):
        tag = str(tag)
        years = ('2004', '2008', '2012', '1998', '1988')
        if any(year in url for year in years):
            return False
        elif 'th colspan="2"' in tag or 'th colspan="3"' in tag:
            return True
        else:
            return False

    if start is None:
        for index, table in enumerate(parser.tables):
            if 'Alabama\xa01' in table.tag.text and 'Alabama\xa06' in table.tag.text:
                start = index
                break
        if not start:
            raise ValueError(f'Could not find suitable start table while download district results: {url}')
    if stop is None:
        # As far as I can tell, there are 50 state tables--one for each state.
        stop = start + 50
    table_range = range(start, stop)

    for index, table in enumerate(parser.tables):
        if index in table_range:
            skip_rows = [0] if header_row_bool(
                url, table.tag) else []  # 2012 has their tables formatted differently. No bonus headers.

            string_output = StringIO()
            table.write(string_output)

            state_table = pd.read_csv(StringIO(string_output.getvalue()), skiprows=skip_rows, index_col=0)

            # Filter out the odd random tables showing party breakdown per state
            # Increase the stop value by one, since we had to skip a table in the middle
            if 'Seats' in state_table.columns or any('United States' in s for s in state_table.columns):
                stop += 1
                table_range = range(start, stop)
                continue

            state_table = state_table.rename(
                index={old: rename_congressional_district(old) for old in state_table.index.values})
            state_table = state_table.drop(labels='', axis='index', errors='ignore')

            if 'Result' in state_table.columns and 'Results' in state_table.columns:
                state_table = state_table.rename(columns={'Results': 'Candidates'})
            state_table = state_table.rename(columns={'Candidates(and run-off results)': 'Candidates'})
            parties = state_table.apply(extract_election_data_series, axis=1)
            state_table = state_table.rename(columns={'First Elected': 'First elected'})
            state_table['First elected'] = state_table['First elected'].apply(handle_first_elected)
            state_table = pd.concat([state_table, parties], axis=1)

            # some year data has the PVI column labeled differently
            alternate_pvi_names = ['2017 PVI', 'Cook PVI (2008)', '2004 CPVI', 'CPVI']
            state_table = state_table.rename(columns={alternate_pvi: 'PVI' for alternate_pvi in alternate_pvi_names})
            # Some years label the district as 'District' and others 'Location'
            # 'Location' is our canonical name
            state_table = state_table.rename(columns={'District': 'Location'})
            state_table = state_table.rename(columns={'Status': 'Results'})
            # Filter out weird incumbent party names (usually vacancies or redistricting)
            party_names = {'Republican', 'Democratic'}
            state_table['Party'] = state_table['Party'].where(state_table['Party'].isin(party_names))
            # print(state_table['Party'].value_counts())

            # Rep names
            rep_name_columns = ['Incumbent', 'Member']
            state_table = state_table.rename(columns={rep: 'Representative' for rep in rep_name_columns})

            pandas_tables_by_state.append(state_table)

    district_df = pd.concat(pandas_tables_by_state)

    # Get rid of duplicate rows, which can happen in redistricting.
    # We only really care about the results, which will be the same in each district
    district_df = district_df[~district_df.index.duplicated(keep='first')]

    assert len(district_df) == 435  # Make sure we ended up with 435 districts
    return district_df


def download_district_results_year(year: int, start: Optional[int] = None, stop: Optional[int] = None):
    district_df = download_district_results(
        url=f'https://en.wikipedia.org/wiki/{year}_United_States_House_of_Representatives_elections',
        start=start,
        stop=stop)
    # district_df = district_df.assign(Year=year)
    district_df['Year'] = year
    district_df['TimeInOffice'] = district_df[['Year', 'First elected']].apply(
        lambda x: 0 if x['First elected'] == -1 else x['Year'] - x['First elected'],
        axis=1)
    district_df = district_df.rename(lambda x: f'{year}-{x}', axis='index')
    return district_df


def load_congressional_district_results_year(year, filename=None) -> pd.DataFrame:
    filename = filename or f'./data/election_results/{year}-congressional-districts.csv'
    return cache_download_csv_to_file(filename)(download_district_results_year)(year)


congressional_district_results = {year: load_congressional_district_results_year(year) for year in range(1972, 2022, 2)}

congressional_district_results_2020 = congressional_district_results[2020]
congressional_district_results_2018 = congressional_district_results[2018]
congressional_district_results_2016 = congressional_district_results[2016]
congressional_district_results_2014 = congressional_district_results[2014]
congressional_district_results_2012 = congressional_district_results[2012]
congressional_district_results_2010 = congressional_district_results[2010]
congressional_district_results_2008 = congressional_district_results[2008]
