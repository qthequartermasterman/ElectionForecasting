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


@cache_download_csv_to_file('data/time_for_change/compiled_time_for_change.csv')
def load_compiled_time_for_change_data():
    """
    Download all the Economic and historical approval data necessary for the Time for Change model.
    :return: DataFrame containing all of the necessary data
    """
    # Download GDP Growth Data
    gdp_growth_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=617&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=GDPC1&scale=left&cosd=1947-01-01&coed=2021-10-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=2&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Quarterly&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=pc1&vintage_date=2022-02-06&revision_date=2022-02-06&nd=1947-01-01'
    gdp_growth_csv = pd.read_csv(gdp_growth_url, index_col='DATE')
    gdp_growth_csv.rename(columns={'GDPC1_PC1': 'GDP Growth'}, inplace=True)
    # gdp_growth_csv

    # Download inflation data
    inflation_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=617&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=MEDCPIM158SFRBCLE&scale=left&cosd=1983-01-01&coed=2021-12-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2022-02-06&revision_date=2022-02-06&nd=1983-01-01'
    inflation_csv = pd.read_csv(inflation_url, index_col='DATE')
    inflation_csv = inflation_csv.rename(columns={'MEDCPIM158SFRBCLE': 'Monthly Inflation YoY'})
    inflation_csv = inflation_csv['Monthly Inflation YoY']
    # inflation_csv

    # Download Presidential Favorability
    approval_url = 'https://news.gallup.com/wwwv7interactives/json/ALLPRESIDENTS/codename.aspx?'
    approval_json = json.loads(requests.get(approval_url).text)
    approval_data = approval_json['AllPresidents']['HistoricalPresident'][0]['data']['Row']
    historical_df = pd.DataFrame(
        list(itertools.chain(*[pres['data']['Row'] for pres in approval_json['AllPresidents']['HistoricalPresident']])))
    # historical_df

    obama_url = 'https://news.gallup.com/wwwv7interactives/json/OBAMAEXPANDED/codename.aspx?'
    obama_json = json.loads(requests.get(obama_url).text)
    obama_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in
                  obama_json['ExpandedDemographics']['data']['date']]
    obama_df = pd.DataFrame(obama_data)
    # obama_df

    trump_url = 'https://news.gallup.com/wwwv7interactives/json/TRUMPEXPANDED/codename.aspx?'
    trump_json = json.loads(requests.get(trump_url).text)
    trump_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in
                  trump_json['ExpandedDemographics']['data']['date']]
    trump_df = pd.DataFrame(trump_data)
    # trump_df

    biden_url = 'https://news.gallup.com/wwwv7interactives/json/CURRENTPRESWEEKLY/codename.aspx?'
    biden_json = json.loads(requests.get(biden_url).text)
    biden_data = [{'StartDate': date['startDate'], 'EndDate': date['endDate'], 'Approve': int(date['Overall']['A']),
                   'Disapprove': int(date['Overall']['D'])} for date in biden_json['CurrentPresident']['data']['date']]
    biden_df = pd.DataFrame(biden_data)
    # biden_df

    combined_approval = pd.concat([biden_df, trump_df, obama_df, historical_df], join='inner', ignore_index=True)
    # combined_approval

    combined_approval['Approve'] = combined_approval['Approve'].apply(int)
    combined_approval['Disapprove'] = combined_approval['Disapprove'].apply(int)
    combined_approval['Net'] = combined_approval['Approve'] - combined_approval['Disapprove']
    # combined_approval

    # Download the popular vote results
    # Results come from here:
    popular_vote_url = 'https://en.wikipedia.org/wiki/List_of_United_States_presidential_elections_by_popular_vote_margin'
    # But it was easier to just modify the table by hand, so it's saved in `data/national_election_winners.csv`

    national_elections = pd.read_csv('data/national_election_winners.csv', index_col='Year')
    # national_elections

    house_url = 'https://en.wikipedia.org/wiki/List_of_United_States_House_of_Representatives_elections,_1856%E2%80%93present'
    # Again this is just easier for me to download ahead of time an manipulate in excel.
    house_results = pd.read_csv('data/house_results.csv', index_col='ElectionYear')

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
        time_for_change = 47.26 + .108 * net_approval + .543 * gdp + 4.313 * incumbent
        months_for_inflation_calc = ('01', '02', '03', '04', '05', '06', '07', '08', '09')
        try:
            inflation_mean = sum(inflation_csv[f'{year}-{month}-01'] for month in months_for_inflation_calc) / len(
                months_for_inflation_calc)
        except KeyError:
            inflation_mean = math.nan
        house_incumbent_result = 100 * house_results['Percentage Incumbent Seats after Election'][year]
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

    compiled_data['Republican TFC'] = compiled_data[['Time For Change Prediction', 'PresidentIncumbentParty']].apply(lambda x: x['Time For Change Prediction'] if x['PresidentIncumbentParty'] == 'Republican' else 100-x['Time For Change Prediction'], axis=1)
    return compiled_data


@cache_download_csv_to_file('data/time_for_change/congressional_time_for_change.csv')
def load_congressional_time_for_change_data():
    time_for_change_data = load_compiled_time_for_change_data()

    def get_series_data_for_year(year):
        return time_for_change_data.loc[year]

    def rename_year(name):
        year, place = name.split('-', maxsplit=1)
        year = str(int(year)+2)
        return '-'.join([year, place])

    def calculate_blowout(percent):
        blow_out_factor = 65
        if percent < 100-blow_out_factor:
            return 'Blow-out D'
        if percent > blow_out_factor:
            return 'Blow-out R'
        else:
            return 'Not Blow-out D'

    combined_congressional_data = pd.concat(list(congressional_district_results.values()))
    district_df = combined_congressional_data[
        ['PVI', 'Party', 'Democratic', 'Republican', 'Libertarian', 'Green', 'Year', 'TimeInOffice']]
    district_df['PreviousRepublican'] = district_df['Republican'].rename(rename_year, axis='index')
    district_df['BlowOut'] = district_df['PreviousRepublican'].apply(calculate_blowout)
    district_df = district_df.reset_index()
    district_df = district_df.rename(columns=({'index': 'Location'}))
    district_df['PVI'] = district_df['PVI'].apply(pvi_to_r_score)
    incumbent_result_columns = ['Party', 'Democratic', 'Republican', 'Libertarian', 'Green']
    district_df['IncumbentResult'] = district_df[incumbent_result_columns].apply(get_incumbent_result, axis=1)
    district_df = district_df[['PVI', 'Location', 'Party', 'IncumbentResult', 'Year', 'Republican', 'TimeInOffice',
                               'PreviousRepublican', 'BlowOut']]
    columns_to_keep = ['GDP', 'Net Approval', 'Incumbent', 'Midterm Year', 'PresidentIncumbentParty',
                       'Time For Change Prediction', 'Republican TFC']
    district_df[columns_to_keep] = district_df[['Year']].apply((lambda x: get_series_data_for_year(x['Year'])), axis=1)[
        columns_to_keep]
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
