from typing import Optional, Union, Tuple

import pandas as pd
import pymc3 as pm

import matplotlib.pyplot as plt
import numpy as np
from arviz import InferenceData


def inv_logit(p: Union[float, np.ndarray]) -> np.ndarray:
    """
    Inverse logit function (i.e. sigmoid function) which maps the reals to a probability
    :param p: any real value to map to a probability
    :return: a probability
    """
    return np.exp(p) / (1 + np.exp(p))


def logit(p: Union[float, np.ndarray]) -> np.ndarray:
    """
    Logit function (i.e. inverse sigmoid) which maps probabilities to the reals
    :param p: any probability to map to the reals
    :return: a real number
    """
    return np.log(p) - np.log(1 - p)


def generate_linzer_model(days: np.ndarray, state_polls: pd.DataFrame, national_polls: np.ndarray, gdp: float,
                          net_approval: float, incumbent: float, president_incumbent_party: str, tune: int = 3000,
                          draws: int = 1000) -> Tuple[pm.Model, InferenceData]:
    """

    :param president_incumbent_party:
    :param gdp:
    :param net_approval:
    :param incumbent:
    :param draws:
    :param tune:
    :param days:
    :param state_polls:
    :param national_polls:
    :return:
    """
    state_observed = state_polls.drop(columns=['PreviousRepublican']).applymap(logit)
    national_observed = logit(national_polls) - state_observed

    with pm.Model() as linzer_model:
        σ_δ = pm.HalfNormal('σ_δ', .01)
        σ_β = pm.HalfNormal('σ_β', .01)
        # τ = pm.Constant('tau', c=20)
        τ = pm.Uniform('τ', lower=10, upper=20)  # This is up to the discretion of the analyst

        # Sampling fundamental priors directly
        # These are hardcoded in using values from time_for_change.ipynb.
        # TODO: Get this distribution automatically
        tfc_intercept = pm.Normal('tfc_Intercept', mu=49.439, sigma=2.332)
        tfc_gdp = pm.Normal('tfc_GDP', mu=0.094, sigma=0.358)
        tfc_net_approval = pm.Normal('tfc_Net_Approval', mu=0.086, sigma=0.051)
        tfc_incumbent = pm.Normal('tfc_Incumbent', mu=2.416, sigma=2.500)
        tfc = pm.Deterministic('tfc',
                               tfc_intercept +
                               tfc_gdp * gdp +
                               tfc_net_approval * net_approval +
                               tfc_incumbent * incumbent
                               )
        tfc_republican = tfc if president_incumbent_party == 'Republican' else 100 - tfc

        fundamental_intercept = pm.Normal('fund_intercept', mu=-1.460050, sigma=0.008357)
        fundamental_tfc_coef = pm.Normal('fund_tfc_coef', mu=0.005842, sigma=0.000164)
        # We set this as constant because the standard deviation is so small we get underflows
        fundamental_prev_repub_coef = 0.023978
        # fundamental_prev_repub_coef = pm.Normal('fund_prev_repub_coef', mu=0.023978, sigma=0.000034)

        for name in state_polls.index:
            unscaled_fundamental_distribution = pm.Deterministic(f'fundamental_{name}',
                                                                 fundamental_intercept +
                                                                 fundamental_tfc_coef * tfc_republican +
                                                                 (fundamental_prev_repub_coef
                                                                  * state_polls.loc[name, 'PreviousRepublican'])
                                                                 )
            fundamental_dist = pm.logit(unscaled_fundamental_distribution / 100)

            β_J = pm.Normal.dist(mu=fundamental_dist, tau=τ)
            print(β_J)
            μ_β = pm.GaussianRandomWalk(f'μ_β_{name}',
                                        sigma=σ_β,
                                        init=β_J,
                                        shape=len(days)
                                        )
            μ_δ = pm.GaussianRandomWalk(f'μ_δ_{name}',
                                        sigma=σ_δ,
                                        shape=len(days)
                                        )
            β = pm.Normal(f'β_{name}', mu=μ_β, sigma=σ_β, observed=state_observed.loc[name].values[::-1])
            δ = pm.Normal(f'δ_{name}', mu=μ_δ, sigma=σ_δ, observed=national_observed.loc[name].values[::-1])
            π = pm.Deterministic(f'π_{name}', pm.invlogit(β + δ))
            # y_k = pm.Binomial('y_k', p=π[-1], n=1000)

        trace: InferenceData = pm.sample(draws=draws,
                                         tune=tune,
                                         return_inferencedata=True)
    return linzer_model, trace


def linzer_model_predict_from_trace(linzer_model: pm.Model,
                                    trace: InferenceData,
                                    name: str) -> np.ndarray:
    """
    Given a Linzer model and a trace (from sampling the given linzer model), make forecast
    :param linzer_model: Pymc3 model for forecasting polls that has been sampled from polling data
    :param trace: The InferenceData of the aforementioned sampling
    :return: numpy array with predictions for each day. Shape=(NUM_TRIALS, NUM_DAYS)
    """
    with linzer_model:
        ppc = pm.sample_posterior_predictive(trace)
    # Since the Beta and Delta (State and National Poll) forecasts work backward in time as they walk, we return the
    # reverse of their sums
    return inv_logit(ppc[f'β_{name}'] + ppc[f'δ_{name}'])[:, ::-1]


def get_final_polls_forecasted(trace: InferenceData, name: str) -> InferenceData:
    """
    Get all of the sampled final polls forecasts from a trace
    :param trace: InferenceData holding the sample data from a PYMC3 forecasting model
    :return: InferenceData containing only the final forecasted polls. Shape=(NUM_CHAINS, NUM_DRAWS)
    """
    # Final Polls
    return trace.posterior[f'π_{name}'][:, :, -1]


# # Probability of greater than 50% of votes
# (final_polls > .5).sum() / final_polls.size


def plot_poll_forecast(days: np.ndarray,
                       poll_forecast: np.ndarray,
                       state_polls: np.ndarray,
                       national_polls: np.ndarray) -> plt.axes:
    """
    Create Matplotlib Axes with a plot of the polls forecast
    :param days: numpy array with all of the day numbers
    :param national_polls: numpy array with the known national poll values for each day
    :param state_polls: numpy array with the known state poll values for each day
    :param poll_forecast: numpy array with the poll forecast values. shape=(NUM_TRIALS, NUM_DAYS)
    :return:
    """
    CI = np.percentile(poll_forecast, axis=0, q=[2.5, 50, 97.5])
    CI50 = np.percentile(poll_forecast, axis=0, q=[25, 50, 75])
    mean = np.mean(poll_forecast, axis=0)

    _, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.fill_between(days, CI[0], CI[2], alpha=0.3, color='b', label='95% CI')
    ax.fill_between(days, CI50[0], CI50[2], alpha=0.3, color='b', label='50% CI')
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, 10))
    ax.plot(CI[1], color='b', label='median')
    ax.plot(mean, color='darkblue', label='mean')
    ax.plot(state_polls, color='darkorange', label='State Polls')
    ax.plot(national_polls, color='purple', label='National Polls')
    ax.legend()
    return ax


if __name__ == '__main__':
    # Sample/Test Data
    sample_days = np.arange(80)
    h = .75
    fundamental = pm.Normal.dist(mu=.6, sigma=.1)
    sample_state_polls1 = np.clip(np.random.normal(h + .01, .01, size=sample_days.size), a_min=0.01, a_max=.99)
    sample_national_polls = np.clip(
        np.random.normal((h - .01) - np.exp(-np.arange(80) / 10), .03, size=sample_days.size), a_min=0.01,
        a_max=.99)
    # We only record state polls (on a 5-day cycle) on days 4, and we don't know the last 10 days
    sample_state_polls1[::5] = None

    # District 2 will be exactly 10 points lower than 1
    sample_state_poll2 = np.clip(sample_state_polls1 - 0.10, a_min=0.01, a_max=.99)


    # Compile all the district data
    district_names = ['District 1', 'District 2']
    sample_state_polls_all = np.stack([sample_state_polls1,
                                       sample_state_poll2]
                                      )

    sample_state_polls_df = pd.DataFrame(data=sample_state_polls_all,
                                         # data=sample_state_polls1.reshape(1, -1),
                                         # index=['District 1'],
                                         index=district_names,
                                         columns=[f'day_{day}' for day in sample_days]
                                         )
    sample_state_polls_df['PreviousRepublican'] = pd.Series(data=['60']*len(district_names),
                                                            index=district_names).astype(float)
    print(sample_state_polls_df)
    # state_polls[-10:] = None
    # We only record national polls (on a 10-day cycle) on days 4,5,6,7,8,9, and we don't know the last 20 days
    sample_national_polls[::10] = None
    sample_national_polls[::5] = None
    sample_national_polls[-20:] = None
    linzer_model, trace = generate_linzer_model(sample_days,
                                                sample_state_polls_df,
                                                sample_national_polls,
                                                gdp=-9.08374,
                                                net_approval=-13,
                                                incumbent=1,
                                                president_incumbent_party='Democratic')
    polls_forecast = linzer_model_predict_from_trace(linzer_model, trace, 'District 1')
    plot = plot_poll_forecast(sample_days,
                              polls_forecast,
                              sample_state_polls1,
                              sample_national_polls)
    plt.show()
