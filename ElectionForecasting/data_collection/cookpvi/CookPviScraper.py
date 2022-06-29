from io import StringIO

import pandas as pd
import requests

states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

district_data_url = 'https://datawrapper.dwcdn.net/01w1c/69/dataset.csv'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'

csv_string = requests.get(district_data_url, headers={'User-Agent': user_agent}).text
csv_string_io = StringIO(csv_string)
cook_pvi_data = pd.read_csv(csv_string_io, header=0, delimiter='\t')

single_district_states = cook_pvi_data['Name'].loc[~cook_pvi_data['Name'].str.contains('-')].index
cook_pvi_data.loc[single_district_states, 'Name'] = cook_pvi_data.loc[single_district_states, 'Name'].astype(str) + '-01'
cook_pvi_data['District'] = cook_pvi_data['Name'].replace(states, regex=True)
cook_pvi_data = cook_pvi_data.set_index('District')
cook_pvi_data['New PVI Raw'] = -cook_pvi_data['New PVI Raw']