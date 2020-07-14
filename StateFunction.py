import random
from Candidate import Candidate
import rcp  # RealClearPolitics poll data
from PollingData import PollingData

class State:
    def __init__(self, name: str, polling_data=None, population=None):
        self.name = name
        self.polling_data = polling_data or PollingData()
        self.population = population or 100

    def get_winner_random(self, candidates: [Candidate]) -> Candidate:
        return random.choice(candidates)

    def get_vote(self, candidates: [Candidate], distribution: [float]) -> Candidate:
        rand_float = random.random()  # Random percentage
        running_total = 0
        for i in range(len(distribution)):
            running_total += distribution[i]
            if rand_float < running_total:
                return candidates[i]
        return Candidate('Write-in', 'I')  # All the other votes must be write-ins

    def get_winner_with_distribution(self, candidates: [Candidate], distribution: [float]) -> Candidate:
        candidate_sums = {}
        for _ in range(self.population):
            vote = self.get_vote(candidates, distribution)
            if vote in candidate_sums:
                candidate_sums[vote] += 1
            else:
                candidate_sums[vote] = 1
        winner = max(candidate_sums, key=candidate_sums.get)
        return winner

    def get_winner(self, candidates: [Candidate]) -> Candidate:
        distribution = self.get_polling_distribution(candidates)
        return self.get_winner_with_distribution(candidates, distribution)

    def get_polling_distribution(self, candidates: [Candidate]) -> [float]:
        return self.polling_data.get_polling_distribtion(self.name, candidates)

    def __repr__(self):
        return self.name
