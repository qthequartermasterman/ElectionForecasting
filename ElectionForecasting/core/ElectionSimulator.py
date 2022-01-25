import asyncio
from collections import defaultdict

from .NationalElection import NationalElection, determine_winner
from .Party import Party
from .PollingData import PollingData
from .State import State, States
from .Candidate import Candidate
from typing import List, Dict, Tuple


class ElectionSimulator:
    """Contains all functionality necessary to run many simulations of a national election."""

    def __init__(self, polling_data=None, parallel=True):
        """

        :param polling_data: a polling data instance.
        :param parallel: bool representing whether or not to run the simulations in parallel.
        """
        self.polling_data = polling_data or PollingData()
        self.parallel = parallel

    async def run_one_simulation(self, candidates: List[Candidate], verbose=True) -> NationalElection:
        election = NationalElection(polling_data=self.polling_data)
        await election.run_election(candidates, verbose=verbose)
        if verbose:
            president = election.president
            vice_president = election.vice_president
            house_majority = election.house_majority
            senate_majority = election.senate_majority
            print(f'President: {president}', f'VP: {vice_president}',
                  f'House: {house_majority}', f'Senate{senate_majority}')
        return election

    async def run_simulations(self, num_simulations: int, candidates: List[Candidate],
                              verbose=False) -> List[NationalElection]:
        """
        Runs the specified number of simulated elections, adds up the number of wins of each candidate, then uses
        that to approximate the probability of a win for each candidate.

        If verbose is specified, it prints each simulation to the console and to disk.

        :param num_simulations: the number of simulations to run
        :param candidates: list of all candidates in the election
        :param verbose: bool that if true, prints the results of each simulated election to console and disk
        :returns a dict containing the number of election wins for each candidate
        """
        return await asyncio.gather(*[self.run_one_simulation(candidates, verbose) for _ in range(num_simulations)])

    @staticmethod
    async def calculate_probabilities(elections: List[NationalElection]) -> \
            Tuple[Dict[Candidate, int], Dict[Candidate, int], Dict[Party, int], Dict[Party, int]]:
        """

        :param elections: List of NationalElections that have been completed.
        :return: (Sums of each president's wins, sums of each VP's wins, sums of each house majority wins, sums of each
        senate majority wins)
        """
        president_sums = defaultdict(lambda: 0)
        vice_president_sums = defaultdict(lambda: 0)
        house_majority_sums = defaultdict(lambda: 0)
        senate_majority_sums = defaultdict(lambda: 0)

        for election in elections:
            president_sums[election.president] += 1
            vice_president_sums[election.vice_president] += 1
            house_majority_sums[election.house_majority] += 1
            senate_majority_sums[election.senate_majority] += 1
        return president_sums, vice_president_sums, house_majority_sums, senate_majority_sums
