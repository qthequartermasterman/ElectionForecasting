from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ElectionForecasting.data_collection.polling.PollsCompiler import PollsCompiler
from ElectionForecasting.data_collection.models.poll_forecasting import (generate_linzer_model,
                                                                         linzer_model_predict_from_trace,
                                                                         plot_poll_forecast)
from ElectionForecasting.data_collection.cookpvi.CookPviScraper import cook_pvi_data


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


STARTING_DATE = date(2022, 6, 1)
ELECTION_DATE = date(2022, 11, 8)
# DATES = list(daterange(STARTING_DATE, ELECTION_DATE))
DATES = list(daterange(STARTING_DATE, STARTING_DATE + timedelta(30)))

compiler = PollsCompiler()

generic_ballot = compiler.obtain_generic_house_poll_timeseries(party='Republican',
                                                               election_date=ELECTION_DATE,
                                                               starting_date=STARTING_DATE
                                                               )
missing_generic_dates = list(set(DATES) - set(generic_ballot.columns))
generic_ballot[missing_generic_dates] = np.NaN

generic_ballot = generic_ballot.loc['Generic Ballot'].sort_index()

house_polls = compiler.obtain_house_poll_timeseries(party='Republican',
                                                    election_date=ELECTION_DATE,
                                                    starting_date=STARTING_DATE
                                                    )
missing_house_dates = list(set(DATES) - set(house_polls.columns))
house_polls[missing_house_dates] = np.NaN
house_polls = house_polls.copy()

house_polls = house_polls.loc[['Florida-13']].sort_index()


# Estimate the Previous Republican result by adding Pres. Trump's percentage to the PVI
previous_republican: pd.DataFrame = cook_pvi_data[['New PVI Raw']] + 46.9
previous_republican = previous_republican.rename(columns={'New PVI Raw': 'PreviousRepublican'})
house_polls = house_polls.join(previous_republican)

house_polls[DATES] = house_polls[DATES].fillna(value=0) + generic_ballot[DATES] + house_polls.loc['Florida-13', 'PreviousRepublican']

assert 'PreviousRepublican' in house_polls.columns

linzer_model, trace = generate_linzer_model(generic_ballot[DATES],
                                            house_polls[['PreviousRepublican', *DATES]],
                                            generic_ballot[DATES],
                                            gdp=-9.08374,
                                            net_approval=-13,
                                            incumbent=1,
                                            president_incumbent_party='Democratic')
if __name__=='__main__':
    polls_forecast = linzer_model_predict_from_trace(linzer_model, trace, 'Florida-13')
    plot = plot_poll_forecast(generic_ballot[DATES],
                              polls_forecast,
                              house_polls[['PreviousRepublican', *DATES]].loc['Florida-13'],
                              generic_ballot[DATES])
    plt.show()
