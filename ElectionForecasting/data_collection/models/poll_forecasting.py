import pymc3 as pm

import matplotlib.pyplot as plt
import numpy as np
from arviz import InferenceData


def inv_logit(p):
    return np.exp(p) / (1 + np.exp(p))


def logit(p):
    return np.log(p) - np.log(1 - p)


def generate_linzer_model(days: np.ndarray,
                          state_polls: np.ndarray,
                          national_polls: np.ndarray,
                          fundamental_distribution: pm.Distribution,
                          tune: int = 3000,
                          draws: int = 1000) -> tuple[pm.Model, InferenceData]:
    """

    :param draws:
    :param tune:
    :param days:
    :param state_polls:
    :param national_polls:
    :param fundamental_distribution:
    :return:
    """
    state_observed = logit(state_polls)
    national_observed = logit(national_polls) - state_observed

    with pm.Model() as linzer_model:
        σ_δ = pm.HalfNormal('σ_δ', .01)
        σ_β = pm.HalfNormal('σ_β', .01)
        # τ = pm.Constant('tau', c=20)
        τ = pm.Uniform('τ', lower=10, upper=20)  # This is up to the discretion of the analyst
        # β_J = pm.Normal('β_J', mu=pm.logit(h), tau=τ)  # Linzer's original starting (constant fundamental)
        # Simulating variable fundamental predictions
        # fundamental_dist = pm.Normal('f', mu=pm.logit(fundamental), sigma=.1)
        fundamental_dist = linzer_model.Var('fundamental', fundamental_distribution)
        β_J = pm.Normal.dist(mu=fundamental_dist, tau=τ)
        μ_β = pm.GaussianRandomWalk('μ_β',
                                    sigma=σ_β,
                                    init=β_J,
                                    shape=len(days)
                                    )
        μ_δ = pm.GaussianRandomWalk('μ_δ',
                                    sigma=σ_δ,
                                    shape=len(days)
                                    )
        β = pm.Normal('β', mu=μ_β, sigma=σ_β, observed=state_observed[::-1])
        δ = pm.Normal('δ', mu=μ_δ, sigma=σ_δ, observed=national_observed[::-1])
        π = pm.Deterministic('π', pm.invlogit(β + δ))
        # y_k = pm.Binomial('y_k', p=π[-1], n=1000)

        trace: InferenceData = pm.sample(draws=draws,
                                         tune=tune,
                                         return_inferencedata=True)
    return linzer_model, trace


def linzer_model_predict_from_trace(linzer_model: pm.Model,
                                    trace: InferenceData) -> np.ndarray:
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
    return inv_logit(ppc['β'] + ppc['δ'])[:, ::-1]


def get_final_polls_forecasted(trace: InferenceData) -> InferenceData:
    """
    Get all of the sampled final polls forecasts from a trace
    :param trace: InferenceData holding the sample data from a PYMC3 forecasting model
    :return: InferenceData containing only the final forecasted polls. Shape=(NUM_CHAINS, NUM_DRAWS)
    """
    # Final Polls
    return trace.posterior['π'][:, :, -1]


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
    days = np.arange(80)
    h = .75
    fundamental = pm.Normal.dist(mu=.6, sigma=.1)
    state_polls = np.clip(np.random.normal(h + .01, .01, size=days.size), a_min=0.01, a_max=.99)
    national_polls = np.clip(np.random.normal((h - .01) - np.exp(-np.arange(80) / 10), .03, size=days.size), a_min=0.01,
                             a_max=.99)
    # We only record national polls (on a 5-day cycle) on days 4, and we don't know the last 10 days
    state_polls[::5] = None
    # state_polls[-10:] = None
    # We only record national polls (on a 10-day cycle) on days 4,5,6,7,8,9, and we don't know the last 20 days
    national_polls[::10] = None
    national_polls[::5] = None
    national_polls[-20:] = None
    linzer_model, trace = generate_linzer_model(days, state_polls, national_polls, fundamental, tune=1000, draws=1000)
    polls_forecast = linzer_model_predict_from_trace(linzer_model, trace)
    plot = plot_poll_forecast(days,
                              polls_forecast,
                              state_polls,
                              national_polls)
    plt.show()
