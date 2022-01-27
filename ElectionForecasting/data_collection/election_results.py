import re
from typing import List, Tuple, Dict, Union, Callable

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
    result_tuples = extract_election_data(district_row['Candidates'])
    return pd.Series(result_tuples)


def download_district_results(url, start, stop) -> pd.DataFrame:
    resp = requests.get(url)
    parser = Parser(resp.text)
    # parser.write_to_dir('./data/election_results')
    pandas_tables_by_state = []

    for index, table in enumerate(parser.tables):
        if index in range(start, stop):
            string_output = StringIO()
            table.write(string_output)
            # pandas_tables_by_state.append(str(string_output.getvalue()))

            state_table = pd.read_csv(StringIO(string_output.getvalue()), skiprows=[0], index_col=0)
            state_table = state_table.rename(
                index={old: rename_congressional_district(old) for old in state_table.index.values})
            parties = state_table.apply(extract_election_data_series, axis=1)
            state_table = pd.concat([state_table, parties], axis=1)

            pandas_tables_by_state.append(state_table)

    return pd.concat(pandas_tables_by_state)


def download_district_results_2020() -> pd.DataFrame:
    return download_district_results(
        url='https://en.wikipedia.org/wiki/2020_United_States_House_of_Representatives_elections',
        start=12,
        stop=62)


def download_district_results_2018() -> pd.DataFrame:
    return download_district_results(
        url='https://en.wikipedia.org/wiki/2018_United_States_House_of_Representatives_elections',
        start=13,
        stop=63)


def download_district_results_2016() -> pd.DataFrame:
    return download_district_results(
        url='https://en.wikipedia.org/wiki/2016_United_States_House_of_Representatives_elections',
        start=12,
        stop=62)


def load_congressional_district_results(filename: str,
                                        download_function: Callable[[], pd.DataFrame]) -> pd.DataFrame:
    """

    :param download_function:
    :param filename:
    :return:
    """
    try:
        district_df = pd.read_csv(filename, index_col=0)
    except FileNotFoundError:
        district_df = download_function()
        district_df.to_csv(filename)
    return district_df


def load_congressional_district_results_2020(filename: str) -> pd.DataFrame:
    return load_congressional_district_results(filename, download_district_results_2020)


def load_congressional_district_results_2018(filename: str) -> pd.DataFrame:
    return load_congressional_district_results(filename, download_district_results_2018)


def load_congressional_district_results_2016(filename: str) -> pd.DataFrame:
    return load_congressional_district_results(filename, download_district_results_2016)


congressional_district_results_2020 = load_congressional_district_results_2020(
    './data/election_results/2020-congressional-districts.csv')
congressional_district_results_2018 = load_congressional_district_results_2018(
    './data/election_results/2018-congressional-districts.csv')
congressional_district_results_2016 = load_congressional_district_results_2016(
    './data/election_results/2016-congressional-districts.csv')

# Tables 12-62 hold the district data by state
# Load tables 13-62 as a dataframe
# Extract the final election data for each district from its final column
# Create a new dataframe with 1 column/party
# Compile all these new dataframes into one master dataframe
