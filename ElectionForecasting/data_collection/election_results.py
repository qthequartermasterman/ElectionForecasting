import re
from typing import List, Tuple, Dict, Union, Callable, Optional

from wikitablescrape.parse import Parser
import requests
from io import StringIO
import pandas as pd


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
    if 'Special' in name:
        name = name.rsplit('Special')[0]
        name = name.strip()
    state, num = name.rsplit(' ', maxsplit=1)
    if 'at-large' in num:
        num = '00'
    if len(num) == 1:
        num = '0' + num
    return state + '-' + num


def extract_election_data(text: str) -> Dict[str, Union[str, float]]:
    """

    :param text:
    :return:
    """
    list_of_results = {}
    if text[:2] == 'Y ':
        text = text[2:]
    if 'round' in text:
        # Instant run-off voting was used. For now ignore the second round.
        # TODO: Capture Instant Run-off results
        text = re.sub(r'\(([0-9.]+%) round 1, [0-9.]+% round 2\)', r'\1', text)
        text = re.sub(r'\(([0-9.]+%) round 1\)', r'\1', text)
    candidates = text.split('% ')
    for candidate in candidates:
        if not candidate:
            break
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
            name, party, percent = name.strip(), party.strip(), 100
        if party in ('Republican', 'Democratic', 'Green', 'Libertarian'):
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

    def header_row_bool(url):
        years = ('2004', '2008', '2012')
        return all(year not in url for year in years)

    skip_rows = [0] if header_row_bool(url) else []  # 2012 has their tables formatted differently. No bonus headers.

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
            string_output = StringIO()
            table.write(string_output)

            state_table = pd.read_csv(StringIO(string_output.getvalue()), skiprows=skip_rows, index_col=0)
            state_table = state_table.rename(
                index={old: rename_congressional_district(old) for old in state_table.index.values})
            parties = state_table.apply(extract_election_data_series, axis=1)
            state_table = pd.concat([state_table, parties], axis=1)

            # some year data has the PVI column labeled differently
            alternate_pvi_names = ['2017 PVI', 'Cook PVI (2008)', '2004 CPVI', 'CPVI']
            state_table = state_table.rename(columns={alternate_pvi: 'PVI' for alternate_pvi in alternate_pvi_names})
            # Some years label the district as 'District' and others 'Location'
            # 'Location' is our canonical name
            state_table = state_table.rename(columns={'District': 'Location'})
            state_table = state_table.rename(columns={'Status': 'Results'})

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
    return district_df


def load_congressional_district_results_year(year, filename=None) -> pd.DataFrame:
    """

    :param year:
    :param filename:
    :return:
    """
    filename = filename or f'./data/election_results/{year}-congressional-districts.csv'
    try:
        district_df = pd.read_csv(filename, index_col=0)
    except FileNotFoundError:
        district_df = download_district_results_year(year)
        district_df.to_csv(filename)
    return district_df


congressional_district_results = {year: load_congressional_district_results_year(year) for year in range(2002, 2022, 2)}

congressional_district_results_2020 = congressional_district_results[2020]
congressional_district_results_2018 = congressional_district_results[2018]
congressional_district_results_2016 = congressional_district_results[2016]
congressional_district_results_2014 = congressional_district_results[2014]
congressional_district_results_2012 = congressional_district_results[2012]
congressional_district_results_2010 = congressional_district_results[2010]
congressional_district_results_2008 = congressional_district_results[2008]
