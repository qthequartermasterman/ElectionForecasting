import numpy as np
import pandas as pd
import arviz as az
from election_results import congressional_district_results_2020
from demographics import congressional_district_demographics
from bambi import Model, Prior
az.style.use('arviz-darkgrid')

parties = ['Democratic', 'Republican', 'Libertarian', 'Green']

# Final combined model
districts_full = pd.concat([congressional_district_demographics, congressional_district_results_2020[parties]],
                           axis=1)

#%%

#%%
# Get rid of NaN
districts_full=districts_full.fillna(0)
districts_full.isna().sum()
# Get rid of apostrophes in the column names
districts_full.columns = districts_full.columns.str.replace("'"," ")
#%%
columns = list(districts_full.columns)
#%%
total = 1000
districts_full[parties] = districts_full[parties]/100  # make the percentages raw decimals
for party in parties:
    districts_full[party+'_y'] = districts_full[party].apply(lambda x:int(x*total))
districts_full['n'] = total
#%%
formula = "p(Republican_y,n) ~ " + ' + '.join([f'"{col}"' for col in columns])
formula
#%%
model_binomial = Model(formula, districts_full, family='binomial')


#%%
def get_priors(column_name):
    if ((column_name != 'Total Population' and 'Population' in column_name) or
            'SEX' in column_name or
            'Poverty' in column_name or
            ('house' in column_name and 'income' not in column_name) or
            'Education' in column_name or
            'Income' in column_name or
            ('UNITS' in column_name and 'Total' not in column_name) or
            column_name in parties
    ):
        return Prior('Beta', alpha=2, beta=2)
    if column_name == 'Cook PVI':
        return Prior('Normal', mu=0, sigma=16)
    else:
        return None

priors = {col: get_priors(col) for col in columns if get_priors(col)}
model_binomial.set_priors(priors)


