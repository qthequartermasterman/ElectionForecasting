from Candidate import Candidate
from PollingData import PollingData
from StateFunction import State
from electoral_votes import electoral_votes


def dict_sum(a, b):
    temp = dict()
    for a_key in a.keys():
        if a_key in b.keys():
            temp[a_key] = a[a_key] + b[a_key]
        else:
            temp[a_key] = a[a_key]
    for b_key in b.keys():
        if b_key not in a.keys():
            temp[b_key] = b[b_key]


class ElectoralCollege:
    def __init__(self, polling_data=None):
        self.electoral_votes = electoral_votes
        self.polling_data = polling_data or PollingData()
        self.states = {name: State(name, self.polling_data) for name in self.electoral_votes.keys()}

    def run_one_simulation(self, candidates: [Candidate]) -> {str: Candidate}:
        winners = {name: state.get_winner(candidates) for name, state in self.states.items()}
        return winners

    def analyze_simulation(self, winners_dict: {str: Candidate}) -> {Candidate: int}:
        candidate_sums = {}
        for state, winner in winners_dict.items():
            if winner in candidate_sums:
                candidate_sums[winner] += self.electoral_votes[state]
            else:
                candidate_sums[winner] = self.electoral_votes[state]
        return candidate_sums

    def get_winner(self, candidate_sums: {Candidate: int}):
        """A candidate needs a simple majority of electoral votes. As there are currently 538 electoral votes,
        that means that a candidate needs 270 to win."""
        # return max(candidate_sums, key=lambda key: candidate_sums[key])
        for cand in candidate_sums.keys():
            if candidate_sums[cand] > 270:
                return cand
        return None

    def run_simulations(self, num_simulations: int, candidates: [Candidate], verbose=False):
        candidate_win_counts = {cand: 0 for cand in candidates}
        candidate_win_counts[None] = 0  # Draws are totally feasible
        candidate_win_counts[Candidate('Write-in', 'I')] = 0
        for i in range(num_simulations):
            results = self.run_one_simulation(candidates)
            candidate_sums = self.analyze_simulation(results)
            candidate_win_counts[self.get_winner(candidate_sums)] += 1
            if verbose:
                print(f'Simulation {i}: ', candidate_sums, 'Winner:', self.get_winner(candidate_sums))

        return candidate_win_counts
