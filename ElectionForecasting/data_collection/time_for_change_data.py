import math
import requests
import json
import itertools
from typing import Dict

import pandas as pd

from DataCollectionUtils import cache_download_csv_to_file
from election_results import congressional_district_results

from datetime import date

party_names = {'Republican', 'Democratic', 'Libertarian', 'Green'}


def pvi_to_r_score(pvi: str) -> int:
    if isinstance(pvi, float):
        return pvi
    if pvi in {'EVEN', 'Even'}:
        return 0
    party, score = pvi.split('+')
    score = int(score)
    return -score if party == 'D' else score


def get_incumbent_result(results: pd.DataFrame):
    for party in party_names:
        if results['Party'] == party:
            return results[party]
    return math.nan


def get_winner(election_series):
    return election_series[list(party_names)].astype(float).idxmax()


def load_national_election() -> pd.DataFrame:
    # Download the popular vote results
    # Results come from here:
    popular_vote_url = 'https://en.wikipedia.org/wiki/List_of_United_States_presidential_elections_by_popular_vote_margin'
    # But it was easier to just modify the table by hand, so it's saved in `data/national_election_winners.csv`
    return pd.read_csv('data/national_election_winners.csv', index_col='Year')


def load_aggregate_house_results() -> pd.DataFrame:
    house_url = 'https://en.wikipedia.org/wiki/List_of_United_States_House_of_Representatives_elections,_1856%E2%80%93present'
    # Again this is just easier for me to download ahead of time and manipulate in excel.
    return pd.read_csv('data/house_results.csv', index_col='ElectionYear')


@cache_download_csv_to_file('data/time_for_change/gdp_growth.csv', refresh_time=24 * 7)
def load_gdp_growth_data() -> pd.DataFrame:
    # Download GDP Growth Data
    gdp_growth_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=617&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=GDPC1&scale=left&cosd=1947-01-01&coed=2021-10-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=2&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Quarterly&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=pc1&vintage_date=2022-02-06&revision_date=2022-02-06&nd=1947-01-01'
    gdp_growth_csv = pd.read_csv(gdp_growth_url, index_col='DATE')
    gdp_growth_csv.rename(columns={'GDPC1_PC1': 'GDP Growth'}, inplace=True)
    return gdp_growth_csv


def load_inflation_data() -> pd.Series:
    # Download inflation data
    inflation_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=617&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=MEDCPIM158SFRBCLE&scale=left&cosd=1983-01-01&coed=2021-12-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2022-02-06&revision_date=2022-02-06&nd=1983-01-01'
    inflation_csv = pd.read_csv(inflation_url, index_col='DATE')
    inflation_csv = inflation_csv.rename(columns={'MEDCPIM158SFRBCLE': 'Monthly Inflation YoY'})
    inflation_csv = inflation_csv['Monthly Inflation YoY']
    return inflation_csv


@cache_download_csv_to_file('data/time_for_change/historical_favorability.csv')
def load_historical_president_favorability() -> pd.DataFrame:
    # Download Presidential Favorability
    approval_url = 'https://news.gallup.com/wwwv7interactives/json/ALLPRESIDENTS/codename.aspx?'
    approval_json = json.loads(requests.get(approval_url).text)
    approval_data = approval_json['AllPresidents']['HistoricalPresident'][0]['data']['Row']
    return pd.DataFrame(
        list(itertools.chain(*[pres['data']['Row'] for pres in approval_json['AllPresidents']['HistoricalPresident']])))


@cache_download_csv_to_file('data/time_for_change/obama_favorability.csv')
def load_obama_favorability() -> pd.DataFrame:
    # Download Obama Favorability
    obama_url = 'https://news.gallup.com/wwwv7interactives/json/OBAMAEXPANDED/codename.aspx?'
    obama_json = json.loads(requests.get(obama_url).text)
    obama_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in
                  obama_json['ExpandedDemographics']['data']['date']]
    return pd.DataFrame(obama_data)


@cache_download_csv_to_file('data/time_for_change/trump_favorability.csv')
def load_trump_favorability() -> pd.DataFrame:
    # Download Trump favorability
    trump_url = 'https://news.gallup.com/wwwv7interactives/json/TRUMPEXPANDED/codename.aspx?'
    trump_json = json.loads(requests.get(trump_url).text)
    trump_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in
                  trump_json['ExpandedDemographics']['data']['date']]
    return pd.DataFrame(trump_data)


@cache_download_csv_to_file('data/time_for_change/biden_favorability.csv', refresh_time=24*7)
def load_biden_favorability() -> pd.DataFrame:
    # Download Biden favorability
    biden_url = 'https://news.gallup.com/wwwv7interactives/json/CURRENTPRESWEEKLY/codename.aspx?'
    biden_json = json.loads(requests.get(biden_url).text)
    biden_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in biden_json['CurrentPresident']['data']['date']]
    return pd.DataFrame(biden_data)


@cache_download_csv_to_file('data/time_for_change/compiled_time_for_change.csv')
def load_compiled_time_for_change_data():
    """
    Download all the Economic and historical approval data necessary for the Time for Change model.
    :return: DataFrame containing all of the necessary data
    """
    # Download GDP Growth Data
    gdp_growth_csv = load_gdp_growth_data()

    # Download inflation data
    inflation_csv = load_inflation_data()

    # Download Presidential Favorability
    historical_df = load_historical_president_favorability()

    # Load Obama favorability
    obama_df = load_obama_favorability()

    # Download Trump favorability
    trump_df = load_trump_favorability()

    # Download Biden favorability
    biden_df = load_biden_favorability()

    # Combine all favorabilities into one dataframe
    combined_approval = pd.concat([biden_df, trump_df, obama_df, historical_df], join='inner', ignore_index=True)
    combined_approval['Approve'] = combined_approval['Approve'].apply(int)
    combined_approval['Disapprove'] = combined_approval['Disapprove'].apply(int)
    combined_approval['Net'] = combined_approval['Approve'] - combined_approval['Disapprove']

    # National Elections
    national_elections = load_national_election()
    aggregate_house_results = load_aggregate_house_results()

    def get_data_for_year(year: int) -> Dict:
        n = 100
        gdp = gdp_growth_csv['GDP Growth'][f'{year}-04-01']
        june_polls = combined_approval.loc[combined_approval['StartDate'].str.contains(f'{year}-06')]
        if not len(june_polls):
            # Use July
            june_polls = combined_approval.loc[combined_approval['StartDate'].str.contains(f'{year}-07')]
        net_approval = june_polls['Net'].iloc[0]
        try:
            pop_vote = round(national_elections['PV %'][year] * n)
        except KeyError:
            pop_vote = math.nan

        previous_presidential_year = year - year % 4 if year % 4 else year - 4
        incumbent = 1 if national_elections['Winner'][previous_presidential_year] != national_elections['Winner'][
            previous_presidential_year - 4] else 0

        # Calculate the Time for Change Prediction using the original coefficients
        time_for_change = 47.26 + .108 * net_approval + .543 * gdp + 4.313 * incumbent

        # Handle inflation calculations
        months_for_inflation_calc = ('01', '02', '03', '04', '05', '06', '07', '08', '09')
        try:
            inflation_mean = sum(inflation_csv[f'{year}-{month}-01'] for month in months_for_inflation_calc) / len(
                months_for_inflation_calc)
        except KeyError:
            inflation_mean = math.nan

        # Incumbent Results
        house_incumbent_result = 100 * aggregate_house_results['Percentage Incumbent Seats after Election'][year]
        midterm_year = int((year % 4) / 2)
        if national_elections['Winner Party'][previous_presidential_year] == 'Rep.':
            presidential_incumbent_party = "Republican"
        elif national_elections['Winner Party'][previous_presidential_year] == 'Dem.':
            presidential_incumbent_party = 'Democratic'
        else:
            presidential_incumbent_party = 'Other'

        return {'GDP': gdp,
                'Net Approval': net_approval,
                'Result': pop_vote,
                'Incumbent': incumbent,
                'n': n,
                'Time For Change Prediction': time_for_change,
                'Avg Inflation': inflation_mean,
                'House Incumbent Percent': house_incumbent_result,
                'Midterm Year': midterm_year,
                'PresidentIncumbentParty': presidential_incumbent_party}

    years_range = range(1948, 2022, 2)
    compiled_data = pd.DataFrame([get_data_for_year(year) for year in years_range], index=years_range)
    compiled_data['Avg Inflation'] = compiled_data['Avg Inflation'].astype('float')

    compiled_data['Republican TFC'] = compiled_data[['Time For Change Prediction', 'PresidentIncumbentParty']].apply(
        lambda x: x['Time For Change Prediction'] if x['PresidentIncumbentParty'] == 'Republican' else 100 - x[
            'Time For Change Prediction'], axis=1)
    return compiled_data


def rename_year(name: str, num_years=2) -> str:
    """Change the year in a Location tag to two years in the future. This is used to transform the
    Election Results to the Previous Election Results for a district."""
    year, place = name.split('-', maxsplit=1)
    year = str(int(year) + num_years)
    return '-'.join([year, place])


def calculate_blowout(republican_percent: float, blow_out_factor: float = 65) -> str:
    """Determine if an election was a republican or democrat blow out or neither."""
    if republican_percent > blow_out_factor:
        return 'Blow-out R'
    if republican_percent < 100 - blow_out_factor:
        return 'Blow-out D'
    else:
        return 'Not Blow-out D'


def calculate_house_pvi(presidential1: float, presidential2: float, house1: float, house2: float) -> float:
    """
    Calculate the "House PVI" metric, which compares how a political entity compares to the national average.

    :param presidential1: Float representing republican result in previous presidential election (national popular vote)
    :param presidential2: Float representing republican result in presidential election (national popular vote) before
        previous
    :param house1: Float representing republican result in previous congressional election (district-level)
    :param house2: Float representing republican result in congressional election (district-level) before previous
    :return: the House PVI metric
    """
    diff1 = house1 - presidential1
    diff2 = house2 - presidential2
    return (diff1 + diff2) / 2


@cache_download_csv_to_file('data/time_for_change/congressional_time_for_change.csv')
def load_congressional_time_for_change_data() -> pd.DataFrame:
    time_for_change_data = load_compiled_time_for_change_data()

    def get_series_data_for_year(year: int) -> pd.Series:
        """Extract the series data for a given year. This is a function for readability."""
        return time_for_change_data.loc[year]

    # Combine all congressional elections into one dataframe
    combined_congressional_data = pd.concat(list(congressional_district_results.values()))
    # Pull only the columns we need later
    district_df = combined_congressional_data[
        ['PVI', 'Party', 'Democratic', 'Republican', 'Libertarian', 'Green', 'Year', 'TimeInOffice']]

    # Add the Previous Republican results in each district and determine if it was a blowout year
    district_df['PreviousRepublican'] = district_df['Republican'].rename(rename_year, axis='index')
    district_df['BlowOut'] = district_df['PreviousRepublican'].apply(calculate_blowout)
    district_df['PreviousRepublican2'] = district_df['Republican'].rename(lambda x: rename_year(x, 4), axis='index')

    # Reset the indices and move the indices to a 'Location' Column
    district_df = district_df.reset_index()
    district_df = district_df.rename(columns=({'index': 'Location'}))

    # Get PVI as a float, if present
    district_df['PVI'] = district_df['PVI'].apply(pvi_to_r_score)

    # Get Incumbent Results
    incumbent_result_columns = ['Party', 'Democratic', 'Republican', 'Libertarian', 'Green']
    district_df['IncumbentResult'] = district_df[incumbent_result_columns].apply(get_incumbent_result, axis=1)

    # Shed off extra columns
    district_df = district_df[['PVI', 'Location', 'Party', 'IncumbentResult', 'Year', 'Republican', 'TimeInOffice',
                               'PreviousRepublican', 'BlowOut']]

    # Fetch Time for Change Data
    tfc_columns_to_keep = ['GDP', 'Net Approval', 'Incumbent', 'Midterm Year', 'PresidentIncumbentParty',
                           'Time For Change Prediction', 'Republican TFC']
    district_df[tfc_columns_to_keep] = district_df[['Year']].apply(lambda x: get_series_data_for_year(x['Year']),
                                                                   axis=1)[tfc_columns_to_keep]
    district_df['PartiesMatch'] = district_df[
        ['Party', 'PresidentIncumbentParty']].apply(lambda x: x['Party'] == x['PresidentIncumbentParty'], axis=1)
    district_df['HouseIncumbentWon'] = district_df['IncumbentResult'] > 50

    return district_df


def load_current_congressional_time_for_change_data():
    year = date.today().year

    # Biden Approval
    biden_url = 'https://news.gallup.com/wwwv7interactives/json/CURRENTPRESWEEKLY/codename.aspx?'
    biden_json = json.loads(requests.get(biden_url).text)
    biden_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in biden_json['CurrentPresident']['data']['date']]
    biden_df = pd.DataFrame(biden_data)
    biden_df['Approve'] = biden_df['Approve'].apply(int)
    biden_df['Disapprove'] = biden_df['Disapprove'].apply(int)
    biden_df['Net'] = biden_df['Approve'] - biden_df['Disapprove']

    # Download the popular vote results
    # Results come from here:
    popular_vote_url = 'https://en.wikipedia.org/wiki/List_of_United_States_presidential_elections_by_popular_vote_margin'
    # But it was easier to just modify the table by hand, so it's saved in `data/national_election_winners.csv`
    national_elections = pd.read_csv('data/national_election_winners.csv', index_col='Year')

    # Download GDP Growth Data
    gdp_growth_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=617&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=GDPC1&scale=left&cosd=1947-01-01&coed=2021-10-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=2&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Quarterly&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=pc1&vintage_date=2022-02-06&revision_date=2022-02-06&nd=1947-01-01'
    gdp_growth_csv = pd.read_csv(gdp_growth_url, index_col='DATE')
    gdp_growth_csv.rename(columns={'GDPC1_PC1': 'GDP Growth'}, inplace=True)

    n = 100
    gdp = gdp_growth_csv['GDP Growth'][-1]
    june_polls = biden_df.loc[pd.to_datetime(biden_df['StartDate']).idxmax()]
    net_approval = june_polls['Net']
    try:
        pop_vote = round(national_elections['PV %'][year] * n)
    except KeyError:
        pop_vote = math.nan

    previous_presidential_year = year - year % 4 if year % 4 else year - 4
    incumbent = 1 if national_elections['Winner'][previous_presidential_year] != national_elections['Winner'][
        previous_presidential_year - 4] else 0
    time_for_change = 47.26 + .108 * net_approval + .543 * gdp + 4.313 * incumbent
    midterm_year = int((year % 4) / 2)

    if national_elections['Winner Party'][previous_presidential_year] == 'Rep.':
        presidential_incumbent_party = "Republican"
    elif national_elections['Winner Party'][previous_presidential_year] == 'Dem.':
        presidential_incumbent_party = 'Democratic'
    else:
        presidential_incumbent_party = 'Other'
    time_for_change = pd.Series({'GDP': gdp,
                                 'Net Approval': net_approval,
                                 'Result': pop_vote,
                                 'Incumbent': incumbent,
                                 'n': n,
                                 'Time For Change Prediction': time_for_change,
                                 'Midterm Year': midterm_year,
                                 'PresidentIncumbentParty': presidential_incumbent_party})

    combined_congressional_data = congressional_district_results[max(congressional_district_results.keys())]
    district_df = combined_congressional_data[['PVI', 'Democratic', 'Republican', 'Libertarian', 'Green', 'Year']]
    district_df['PVI'] = district_df['PVI'].apply(pvi_to_r_score)
    district_df['Party'] = district_df[list(party_names)].apply(get_winner, axis=1)
    district_df = district_df[['PVI', 'Party', 'Year', 'Republican']]
    district_df['Republican TFC'] = district_df[['Time For Change Prediction', 'PresidentIncumbentParty']].apply(
        lambda x: x['Time For Change Prediction'] if x['PresidentIncumbentParty'] == 'Republican' else 100 - x[
            'Time For Change Prediction'], axis=1)
    columns_to_keep = ['GDP', 'Net Approval', 'Incumbent', 'Midterm Year', 'PresidentIncumbentParty',
                       'Time For Change Prediction', 'Republican TFC']
    district_df[columns_to_keep] = district_df[['Year']].apply(lambda _: time_for_change, axis=1)[
        columns_to_keep]
    district_df['PartiesMatch'] = district_df[
        ['Party', 'PresidentIncumbentParty']].apply(lambda x: x['Party'] == x['PresidentIncumbentParty'], axis=1)
    return district_df
