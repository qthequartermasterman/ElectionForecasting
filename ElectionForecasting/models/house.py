from datetime import date

import matplotlib.pyplot as plt

from ElectionForecasting.data_collection.polling.PollsCompiler import PollsCompiler
from ElectionForecasting.data_collection.models.poll_forecasting import (generate_linzer_model,
                                                                         linzer_model_predict_from_trace,
                                                                         plot_poll_forecast)

STARTING_DATE = date(2022, 3, 13)
ELECTION_DATE = date(2022, 11, 8)

compiler = PollsCompiler()

generic_ballot = compiler.obtain_generic_house_poll_timeseries(party='Republican',
                                                               election_date=ELECTION_DATE,
                                                               starting_date=STARTING_DATE
                                                               ).loc['Generic Ballot']


house_polls = compiler.obtain_house_poll_timeseries(party='Republican',
                                                    election_date=ELECTION_DATE,
                                                    starting_date=STARTING_DATE
                                                    )


# assert 'PreviousRepublican' in house_polls.columns

linzer_model, trace = generate_linzer_model(generic_ballot,
                                            house_polls,
                                            generic_ballot,
                                            gdp=-9.08374,
                                            net_approval=-13,
                                            incumbent=1,
                                            president_incumbent_party='Democratic')
