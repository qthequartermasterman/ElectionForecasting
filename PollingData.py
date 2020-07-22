import csv
import os
import random
import time
import urllib.request

#import rcp

from Candidate import Candidate
from electoral_votes import electoral_votes


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

        self.margin_of_error = .05

    def download_five_thirty_eight_data(self):
        """Downloads the most recent polling data from fivethirtyeight's github page.
        The URL is stored in self.fivethirtyeight_polling_data_url

        Takes no parameters and returns nothing."""
        if not os.path.exists(self.local_uri_538) or time.time() - os.path.getmtime(self.local_uri_538) > 86400:
            # Update files that don't exist or that are older than 86400s (24 hrs).
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
                    self.results2016[row['State']] = {'D': row['D'], 'R': row['R']}
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
                poll = .75 * polls_data + .25 * self.estimate_polls(state_name, candidate)
            else:
                poll = self.estimate_polls(state_name, candidate)
            if noise:
                poll += self.margin_of_error * random.gauss(0, 1) / 2
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

    def estimate_polls(self, state_name: str, candidate: Candidate):
        """In instances where polling data does not currently exist for a state, we can estimate it using historical
        trends, correlated states, and/or the national average.

        As currently implemented, it simply gives the national average for a candidate.
        TODO: implement state correlation and historical trends

        :param state_name: a string containing the name of the state whose estimated polling average we want
        :param candidate: a Candidate object representing the candidate

        :returns: a float between 0 and 1 representing the estimated polling percentage"""

        polling_dictionary = self.get_polling_dictionary()
        results2016 = self.fill_2016_results()

        if candidate.party in ['D', 'R']:
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
