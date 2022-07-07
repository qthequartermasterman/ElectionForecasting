from datetime import date, timedelta

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from ElectionForecasting.data_collection.DataCollectionUtils import daterange
from ElectionForecasting.data_collection.models.poll_forecasting import generate_linzer_model, \
    linzer_model_predict_from_trace, plot_poll_forecast
from ElectionForecasting.data_collection.polling.PollsCompiler import PollsCompiler
from ElectionForecasting.data_collection.cookpvi.CookPviScraper import cook_pvi_data

STARTING_DATE = date(2022, 6, 1)
ELECTION_DATE = date(2022, 11, 8)
# DATES = list(daterange(STARTING_DATE, ELECTION_DATE))
# DATES = list(daterange(STARTING_DATE, STARTING_DATE + timedelta(30), timedelta(7)))

compiler = PollsCompiler()

# generic_ballot = compiler.obtain_generic_house_poll_timeseries(party='Republican',
#                                                                election_date=ELECTION_DATE,
#                                                                starting_date=STARTING_DATE
#                                                                )
# missing_generic_dates = list(set(DATES) - set(generic_ballot.columns))
# generic_ballot[missing_generic_dates] = np.NaN
#
# generic_ballot = generic_ballot.loc['Generic Ballot'].sort_index()
#
# house_polls = compiler.obtain_house_poll_timeseries(party='Republican',
#                                                     election_date=ELECTION_DATE,
#                                                     starting_date=STARTING_DATE
#                                                     )
# missing_house_dates = list(set(DATES) - set(house_polls.columns))
# house_polls[missing_house_dates] = np.NaN
# house_polls = house_polls.copy()
#
# house_polls = house_polls.loc[['Florida-13']].sort_index()

house_polls = compiler.obtain_house_poll_timeseries(party='Republican',
                                                    election_date=ELECTION_DATE,
                                                    starting_date=STARTING_DATE
                                                    )
house_polls = house_polls.drop(columns=[col for col in house_polls.columns if col > STARTING_DATE+timedelta(60)])


generic_ballot = compiler.obtain_generic_house_poll_timeseries(party='Republican',
                                                               election_date=ELECTION_DATE,
                                                               starting_date=STARTING_DATE
                                                               )
generic_ballot = compiler.interpolate_district_polls(generic_ballot, ELECTION_DATE)
generic_ballot = compiler.window_district_timeseries(generic_ballot)
generic_ballot = generic_ballot.drop(columns=[col for col in generic_ballot.columns if col > STARTING_DATE+timedelta(60)
                                              ])


# Estimate the Previous Republican result by adding Pres. Trump's 2020 percentage to the PVI
previous_republican: pd.DataFrame = cook_pvi_data[['New PVI Raw']] + 46.9
previous_republican = previous_republican.rename(columns={'New PVI Raw': 'PreviousRepublican'})
house_polls = house_polls.join(previous_republican)
house_polls = house_polls.loc[['Florida-13']]

# house_polls[DATES] = house_polls[DATES].fillna(value=0) + generic_ballot[DATES] + house_polls.loc['Florida-13', 'PreviousRepublican']

assert 'PreviousRepublican' in house_polls.columns

print(generic_ballot)
print(house_polls)


if __name__=='__main__':
    linzer_model, trace = generate_linzer_model(generic_ballot,
                                                house_polls,
                                                generic_ballot,
                                                gdp=-9.08374,
                                                net_approval=-13,
                                                incumbent=1,
                                                president_incumbent_party='Democratic')

    polls_forecast = linzer_model_predict_from_trace(linzer_model, trace, 'Florida-13')
    plot = plot_poll_forecast(generic_ballot,
                              polls_forecast,
                              house_polls.loc['Florida-13'],
                              generic_ballot)
    plt.show()
