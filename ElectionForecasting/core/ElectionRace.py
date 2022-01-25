import random
from collections import defaultdict
from enum import Enum
from typing import Sequence, Dict, Iterable
from dataclasses import dataclass

from .Candidate import Candidate
from .Party import WriteIn, RepublicanParty, DemocratParty
from .PollingData import PollingData
from .State import States


class ElectionType(Enum):
    UniformRandomDistribution = 0
    PollingDistribution = 1


ElectionResult = Dict[Candidate, int]  # Dict of candidates whose values are the candidate's vote count


class ElectionRace:
    def __init__(self, state: States, district_num: int, polling_data: PollingData = None, population: int = None):
        """
        :param name: str representing the name of the particular election race
        :param polling_data: PollingData
        object containing all of the polling data needed to perform the simulation (optional)
        :param population: int
        representing the voting population in the election. When this has the same order of magnitude as the real
        voting population and/or the same precision as the polling data, then estimations/simulations will be more
        precise. (optional)
        """
        self.name: str = f'{state.value.abbreviation}-{district_num}'
        self.state = state
        self.district_num = district_num
        self.polling_data: PollingData = polling_data or PollingData()
        self.population: int = population or 250

    async def get_winner_random(self, candidates: Sequence[Candidate]) -> ElectionResult:
        """
        Chooses a random candidate as winner with uniform distribution. No weighting is used.
        :param candidates: Sequence (such as list) of candidates in the race.
        :returns: the winning candidate
        """
        return {candidate: self.population if candidate == random.choice(candidates) else 0 for candidate in candidates}

    async def get_vote(self, candidates_distribution: Dict[Candidate, float]) -> Candidate:
        """
        Simulate one voter with their given voting probabilities.
        :param candidates_distribution: Dict. Keys are candidates, values are floats representing percentage of
        the voting population that is polling for them.
        :return: the candidate that this voter voted for
        """
        rand_float = random.random()  # Random percentage
        running_total = 0
        for candidate, percentage in candidates_distribution.items():
            running_total += percentage
            if rand_float < running_total:
                return candidate
        # If this voter did not pick any of the running candidates, they must be a Write-In
        return Candidate('Write-in', WriteIn)

    async def get_winner_with_distribution(self, candidates_distribution: Dict[Candidate, float]) -> ElectionResult:
        """
        Simulate the winner of this race using a given polling/statistics distribution.
        :param candidates_distribution: dict whose keys are candidates and values are their corresponding polling
        percentages
        :return: the candidate who received the most votes in this simulation
        """
        candidate_sums = defaultdict(lambda: 0)  # Defaultdict so that if a candidate is missing, they have 0 votes
        for _ in range(self.population):  # Cast and record a vote for every voter
            vote = await self.get_vote(candidates_distribution)
            candidate_sums[vote] += 1
        winner = max(candidate_sums, key=candidate_sums.get)  # Pick the winner
        if winner.party not in [DemocratParty, RepublicanParty]:  # If a 3rd party wins, then note this in the console.
            print(f'\n\t{winner} won {self.name}, with distribution:')
            print('\t', candidate_sums)
            print('\tPercentage:',
                  {key: f'{round(100 * value / sum(candidate_sums.values()), 2)}%' for key, value in
                   candidate_sums.items()})
            print('\tPolling Data:', candidates_distribution)
        return candidate_sums

    async def get_winner(self, candidates: Sequence[Candidate],
                         simulation_type: ElectionType = ElectionType.PollingDistribution) -> ElectionResult:
        """
        Simulate the winner of this race using the given simulation type.
        :param simulation_type: ElectionType representing the type of simulation to run.
        :param candidates: sequence (such as list) of candidates.
        :return: the winner of the simulated election
        """
        if simulation_type == ElectionType.UniformRandomDistribution:
            return await self.get_winner_random(candidates)
        elif simulation_type == ElectionType.PollingDistribution:
            candidates_distribution: Dict[Candidate, float] = await self.get_polling_distribution(candidates)
            return await self.get_winner_with_distribution(candidates_distribution)
        else:
            raise ValueError(f'Invalid simulation type: {simulation_type}.')

    async def get_polling_distribution(self, candidates: [Candidate]) -> Dict[Candidate, float]:
        """
        Pull the given candidates polling distribution from the PollingData
        :param candidates: sequence (such as list) of candidates.
        :return: dict whose keys are candidates and values are their corresponding polling
        percentages
        """
        return self.polling_data.get_polling_distribtion(self.state, self.district_num, candidates)

    def __repr__(self):
        return self.name
