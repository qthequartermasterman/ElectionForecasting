import csv
import os
import random
import time
import urllib.request

import rcp

from Candidate import Candidate
from electoral_votes import electoral_votes


class PollingData:
    """Handles downloading and sorting all the polling data from various sources online."""

    def __init__(self):
        self.fivethirtyeight_polling_data_url = 'https://projects.fivethirtyeight.com/2020-general-data/presidential_poll_averages_2020.csv'
        self.local_uri_538 = 'data/fivethirtyeight.csv'
        self.local_uri_2016_results = 'data/2016results.csv'

        # electoral_votes is a dict with state names as keys, we also want the National Poll data, for good measure
        self.list_of_state_names = list(electoral_votes.keys()) + ['National']
        self.polling_dictionary = {}
        self.results2016 = {}

        self.margin_of_error = .05

    def download_five_thirty_eight_data(self):
        if not os.path.exists(self.local_uri_538) or time.time() - os.path.getmtime(self.local_uri_538) > 86400:
            # Update files that don't exist or that are older than 86400s (24 hrs).
            # If it exits and is not old, then we shouldn't download it again.
            urllib.request.urlretrieve(self.fivethirtyeight_polling_data_url, self.local_uri_538)

    def fill_538_polling_dictionary(self):
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

    def get_polling_data(self):
        self.fill_538_polling_dictionary()
        return self.polling_dictionary

    def get_polling_distribtion(self, state_name: str, candidates: [Candidate], noise=True) -> [float]:
        """:returns: [float] with the polling average as a decimal between 0 and 1 of each candidate in the
        same order as candidates"""
        polling_dictionary = self.get_polling_data()
        distribution = []
        for candidate in candidates:
            if (state_name, candidate.name) in polling_dictionary.keys():
                poll = polling_dictionary[(state_name, candidate.name)]
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

    def estimate_polls(self, state_name: str, candidate: Candidate):
        """In instances where polling data does not currently exist for a state, we can estimate it using historical
        trends, correlated states, and/or the national average.

        As currently implemented, it simply gives the national average for a candidate.
        TODO: implement state correlation and historical trends

        :param state_name: a string containing the name of the state whose estimated polling average we want
        :param candidate: a Candidate object representing the candidate

        :returns: a float between 0 and 1 representing the estimated polling percentage"""

        polling_dictionary = self.get_polling_data()
        results2016 = self.fill_2016_results()

        if candidate.party in ['D', 'R']:
            previous_result = results2016[state_name][candidate.party]
            return float(previous_result)
        else:
            national_polling_average = polling_dictionary[('National', candidate.name)]
            return national_polling_average
