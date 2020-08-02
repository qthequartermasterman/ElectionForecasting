import csv
import os
import random
import time
from datetime import date
import urllib.request
import math

#import rcp

from Candidate import Candidate
from electoral_votes import electoral_votes
import numpy as np


class PollingData:
    """Handles downloading and sorting all the polling data from various sources online."""

    def __init__(self):
        self.fivethirtyeight_polling_data_url = 'https://projects.fivethirtyeight.com/2020-general-data/presidential_poll_averages_2020.csv'
        self.local_uri_538 = 'data/fivethirtyeight.csv'
        self.local_uri_2016_results = 'data/2016results.csv'
        self.local_uri_similarity = 'data/StateSimilarityClosest.csv'

        # electoral_votes is a dict with state names as keys, we also want the National Poll data, for good measure
        self.list_of_state_names = list(electoral_votes.keys()) + ['National']
        self.polling_dictionary = {}
        self.results2016 = {}
        self.similar_states = {}

        self.margin_of_error = .04
        self.bayesian_sd_polls = 0

    def download_five_thirty_eight_data(self):
        """Downloads the most recent polling data from fivethirtyeight's github page.
        The URL is stored in self.fivethirtyeight_polling_data_url

        Takes no parameters and returns nothing."""
        midnight_this_morning = (int(time.time() // 86400)) * 86400
        if not os.path.exists(self.local_uri_538) or os.path.getmtime(self.local_uri_538) < midnight_this_morning:
            # Update files that don't exist or that are older than midnight
            # If it exits and is not old, then we shouldn't download it again.
            urllib.request.urlretrieve(self.fivethirtyeight_polling_data_url, self.local_uri_538)

    def fill_538_polling_dictionary(self) -> {(str, str): float}:
        """Converts the fivethirtyeight polling data stored on disk to a python dictionary in memory for later use.
        Takes no parameters.
        :returns the dictionary with the polling data"""
        if not len(self.polling_dictionary):
            self.download_five_thirty_eight_data()
            with open(self.local_uri_538, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (row['state'], row['candidate_name']) not in self.polling_dictionary.keys():
                        # Fivethirtyeight reports Nebraska as 'NE-2', since it has multiple electoral districts
                        if row['state'] == 'NE-2':
                            state_name = 'Nebraska'
                        else:
                            state_name = row['state']
                        candidate_name = row['candidate_name']
                        polling_average = float(row['pct_trend_adjusted']) / 100
                        self.polling_dictionary[(state_name, candidate_name)] = polling_average
        return self.polling_dictionary

    def fill_state_similarity(self) -> {str: (str, str, str)}:
        if not len(self.similar_states):  # We don't need to reload if it's already loaded
            with open(self.local_uri_similarity, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['State'] not in self.similar_states.keys():
                        #
                        state_name = row['State']
                        closest1 = row['Closest1']
                        closest2 = row['Closest2']
                        closest3 = row['Closest3']
                        self.similar_states[state_name] = (closest1, closest2, closest3)
        return self.similar_states

    def fill_2016_results(self):
        if not len(self.results2016):
            with open(self.local_uri_2016_results, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.results2016[row['State']] = {'D': row['D'], 'R': row['R'], 'L': row['L'], 'G': row['G']}
        return self.results2016

    def fill_rcp_polling_dictionary(self, candidates):
        # Try RealClearPolitics for polling data
        for state in set(self.list_of_state_names).difference([key[0] for key in self.polling_dictionary.keys()]):
            for candidate in candidates:
                raw_polling_data = rcp.get_polls(candidate=candidate.name, state=state)
                if len(raw_polling_data):
                    poll_url = raw_polling_data[0]['url']
                    polls_data = rcp.get_poll_data(poll_url)[0]['data']
                    for poll in polls_data:
                        if poll['Poll'] == 'RCP Average':
                            for cand in candidates:
                                if f'{cand.short_name} ({cand.party})' in poll.keys():
                                    self.polling_dictionary[(state, cand.name)] = float(poll[str(cand)]) / 100
        return self.polling_dictionary

    def get_polling_dictionary(self):
        self.fill_538_polling_dictionary()
        return self.polling_dictionary

    def get_polling_data(self, state_name: str, candidate: Candidate):
        polling_dictionary = self.get_polling_dictionary()
        if (state_name, candidate.name) in polling_dictionary.keys():
            return polling_dictionary[(state_name, candidate.name)]
        else:
            return None

    def get_polling_distribtion(self, state_name: str, candidates: [Candidate], noise=True) -> [float]:
        """:returns: [float] with the polling average as a decimal between 0 and 1 of each candidate in the
        same order as candidates"""
        polling_dictionary = self.get_polling_dictionary()
        distribution = []
        for candidate in candidates:

            polls_data = self.get_polling_data(state_name, candidate)
            if polls_data:
                poll = .80 * polls_data + .20 * self.estimate_polls(state_name, candidate)
            else:
                poll = self.estimate_polls(state_name, candidate)
            if noise:
                poll += self.margin_of_error * random.gauss(0, 1) / 2

            #poll = self.estimate_polls_bayesian(state_name, candidate)
            distribution.append(poll)

            '''
            # Try RealClearPolitics for polling data
            poll_url = rcp.get_polls(candidate=candidate.name, state=self.name)[0]['url']
            polls_data = rcp.get_poll_data(poll_url)[0]['data']
            for poll in polls_data:
                if poll['Poll'] == 'RCP Average':
                    for cand in candidates:
                        if str(cand) in poll.keys():
                            distribution.append(float(poll[str(cand)]) / 100)
                        else:
                            distribution.append(0)
                    return distribution
            '''
        return distribution

    def get_average_of_similar_states(self, state_name: str, candidate: Candidate):
        similar_states = self.fill_state_similarity()
        similar_states_tuple = similar_states[state_name]
        similar_state_polls = [float(self.get_polling_data(state, candidate)) for state in similar_states_tuple if
                               self.get_polling_data(state, candidate)]
        if len(similar_state_polls):
            average_of_similar_states = sum(similar_state_polls) / len(similar_state_polls)
            # Take a weighted average where half of the estimate comes from the previous election and
            # half of the estimate comes from current polls in similar states
            return average_of_similar_states
        else:
            return None

    def estimate_polls(self, state_name: str, candidate: Candidate) -> float:
        """In instances where polling data does not currently exist for a state, we can estimate it using historical
        trends, correlated states, and/or the national average.

        As currently implemented, it simply gives the national average for a candidate.
        TODO: implement state correlation and historical trends

        :param state_name: a string containing the name of the state whose estimated polling average we want
        :param candidate: a Candidate object representing the candidate

        :returns: a float between 0 and 1 representing the estimated polling percentage"""

        polling_dictionary = self.get_polling_dictionary()
        results2016 = self.fill_2016_results()

        if candidate.party in ['D', 'R', 'L', 'G']:
            previous_result = float(results2016[state_name][candidate.party])
            average_of_similar_states = self.get_average_of_similar_states(state_name, candidate)
            if average_of_similar_states:
                # Take a weighted average where half of the estimate comes from the previous election and
                # half of the estimate comes from current polls in similar states
                return .5 * previous_result + .5 * average_of_similar_states
            else:
                return previous_result
        else:
            national_polling_average = polling_dictionary[('National', candidate.name)]
            return national_polling_average

    def get_standard_deviation_of_polls(self, day=date.today()):
        """Linear Interpolatation of emperical standard deviations of how polling data predicts the result
        on a given date.

        Calculated in the original paper using partial pooled historical data. Instead of recreating that, we
        interpolate their data.

        Based on methodology described in "Bayesian Combination of State Polls and Election Forecasts" (Lock & Gelman 2010)
        TODO: Although Section 2 of Lock&Gelman suggests this is how they perform their simulations, the actual results in Section 4 suggest this depends on the state

        Lock, Kari, and Andrew Gelman. "Bayesian combination of state polls and election forecasts." Political Analysis
        18.3 (2010): 337-348.

        :param day: datetime.date of the day of the poll
        :return: stanard deviation of how the poll predicts the final result
        """
        if self.bayesian_sd_polls:
            return self.bayesian_sd_polls
        else:
            election = date(2020, 11, 3)
            days_to_election = (election - day).days  # Number of days until the election
            dates = np.array([(election - date(2020, 11, 1)).days,
                              (election - date(2020, 8, 1)).days,
                              (election - date(2020, 5, 1)).days,
                              (election - date(2020, 2, 1)).days])
            sd_to_interpolate = np.array([.014, .022, .03, .038])
            self.bayesian_sd_polls = float(np.interp(days_to_election, dates, sd_to_interpolate))
            return self.bayesian_sd_polls


    def estimate_polls_bayesian(self, state_name: str, candidate: Candidate) -> float:
        """

        Based on methodology described in "Bayesian Combination of State Polls and Election Forecasts" (Lock & Gelman 2010)

        Lock, Kari, and Andrew Gelman. "Bayesian combination of state polls and election forecasts." Political Analysis
        18.3 (2010): 337-348.

        :param state_name: a string containing the name of the state whose estimated polling average we want
        :param candidate: a Candidate object representing the candidate
        :returns: a float between 0 and 1 representing the estimated polling percentage"""
        results2016 = self.fill_2016_results()

        if candidate.party in ['D', 'R']:
            current_state_poll = self.get_polling_data(state_name, candidate)
            current_national_poll = self.get_polling_data('National', candidate)
            if current_state_poll is None:
                return self.estimate_polls(state_name, candidate)
            # We can use bayesian updating using weighted poll data.
            # For more details see Equation (5) in Lock&Gelman

            previous_state = float(results2016[state_name][candidate.party])
            previous_national = float(results2016['National'][candidate.party])
            d2016 = previous_state - previous_national

            var_poll_given_result = self.get_standard_deviation_of_polls() ** 2  # Square of the interpolated SD
            #var_poll_given_result = .06 ** 2
            var_result = .033 ** 2  # Currently just the empirical SD that Lock&Gelman found by simulation.
            # TODO: Calculate a var_result independently

            mean_numerator = (current_state_poll/var_poll_given_result + (d2016 + current_national_poll)/var_result)
            mean_denominator = (1/var_poll_given_result + 1/var_result)
            mean = mean_numerator/mean_denominator
            variance = 1/(1/var_poll_given_result + 1/var_result)
            sd = math.sqrt(variance)
            return random.gauss(mean, sd)
        else:
            return self.estimate_polls(state_name, candidate)