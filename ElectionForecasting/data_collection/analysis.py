# %%
import numpy as np
import pandas as pd

from election_results import congressional_district_results_2020
from demographics import congressional_district_demographics

# %%


# %%

list(congressional_district_demographics.columns)

# %%

congressional_district_demographics = congressional_district_demographics[
    ~congressional_district_demographics['Cook PVI'].isna()]

# %%

congressional_district_demographics[['Cook PVI', 'Male Population']].isna().sum()

# %%

congressional_district_results_2020['Republican'].isna().sum()

# %%

congressional_district_results_2020['Republican']

# %%

from sklearn.impute import SimpleImputer

zero_imputer = SimpleImputer(strategy='constant')
imputed_repub = zero_imputer.fit_transform(congressional_district_results_2020[['Republican']])

# %%

congressional_district_results_2020['Republican'] = pd.DataFrame(imputed_repub,
                                                                 index=list(congressional_district_demographics.index))
congressional_district_results_2020['Republican']

# %%

districts = pd.concat([congressional_district_demographics, congressional_district_results_2020], axis=1)

# %%

districts['Republican'].isna().sum()

# %%

df = districts[['Cook PVI', 'Male Population']]
df.describe()
# %%
normalized = (df - df.mean()) / df.std()
normalized.describe()

# %%

from sklearn.linear_model import BayesianRidge
from sklearn.linear_model import ARDRegression

# repub = BayesianRidge(tol=1e-10)
repub = ARDRegression()
repub.fit(normalized, districts['Republican'])

# %%

repub.coef_

# %%

repub.predict([[-2, 0]])

# %%

districts = districts.rename(columns={'Male Population': 'MalePopulation', 'Cook PVI': 'CookPVI'})
districts['Republican'] = districts['Republican'] / 100
districts['Democratic'] = districts['Democratic'] / 100
districts['Libertarian'] = districts['Libertarian'] / 100
# %%

from bambi import Model
import arviz as az

# %%
prior = {'MalePopulation': 'beta',
         'CookPVI': 'gaussian'}
model = Model("Republican ~ MalePopulation + CookPVI", districts, family='binomial')
# %%
model
# %%
results = model.fit()
# %%
model.plot_priors()
# %%
az.plot_trace(results)
az.summary(results)
# %%
test_data = pd.DataFrame({'MalePopulation': np.linspace(0, 1, 1000),
                          'CookPVI': np.linspace(-10, 10, 1000)})

predictions = model.predict(results, data=test_data, kind='pps', inplace=False)
predictions
# %%
az.style.use('arviz-darkgrid')
az.plot_forest([predictions])
# %%
# %%
