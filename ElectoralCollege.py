from Candidate import Candidate
from PollingData import PollingData
from StateFunction import State
from electoral_votes import electoral_votes, total_electoral_votes
from datetime import date

from multiprocessing import Pool
from os import cpu_count


NUM_CPU = cpu_count()


def dict_sum(a, b):
    """Adds together the values of matching keys of two dictionaries.
    :param a: first dict to add
    :param b: second dict to add

    :returns dictionary with added values for duplicate keys and the value of singular keys"""
    temp = dict()
    for a_key in a.keys():
        if a_key in b.keys():
            temp[a_key] = a[a_key] + b[a_key]
        else:
            temp[a_key] = a[a_key]
    for b_key in b.keys():
        if b_key not in a.keys():
            temp[b_key] = b[b_key]
    return temp


class ElectoralCollege:
    """Contains all functionality necessary to simulate the electoral college."""
    def __init__(self, polling_data=None):
        self.electoral_votes = electoral_votes
        self.polling_data = polling_data or PollingData()
        self.states = {name: State(name, self.polling_data) for name in self.electoral_votes.keys()}

    def run_one_simulation(self, candidates: [Candidate]) -> {str: Candidate}:
        """Runs a single electoral college simulation. For each state, it generates a single winner

        :param candidates: a list of candidates
        :returns a dictionary with the names of states as keys and the winner of each state as values"""
        winners = {name: state.get_winner(candidates) for name, state in self.states.items()}
        return winners

    def analyze_simulation(self, winners_dict: {str: Candidate}, verbose=True) -> {Candidate: int}:
        """Given the winner of each state, gives the total electoral votes of each candidate. Additionally prints to the

        :param winners_dict: a dictionary with state names as keys and candidates as values
        :param verbose: a bool. When true, prints to the console when an independent or third party wins a stat
        :returns a dict with Candidates as keys and their corresponding electoral vote totals as values"""
        candidate_sums = {}
        for state, winner in winners_dict.items():
            if winner in candidate_sums:
                candidate_sums[winner] += self.electoral_votes[state]
            else:
                candidate_sums[winner] = self.electoral_votes[state]
            if verbose:
                if winner.party not in ['D', 'R']:
                    print(f'\t{winner} won {state}, with {self.electoral_votes[state]} electoral votes.')
        return candidate_sums

    def get_winner(self, candidate_sums: {Candidate: int}):
        """A candidate needs a simple majority of electoral votes. As there are currently 538 electoral votes,
        that means that a candidate needs 270 to win.
        :param candidate_sums: dict with the number of electoral votes for each candidate
        :returns the candidate who won the election, or None if no candidate achieved a majority"""
        # return max(candidate_sums, key=lambda key: candidate_sums[key])
        for cand in candidate_sums.keys():
            if candidate_sums[cand] > total_electoral_votes/2:
                return cand
        return None

    def save_simulation_to_csv(self, candidates: [Candidate], candidate_sums: {Candidate: int}, winner: Candidate,
                               state_results: {str: Candidate}, simulation_number=-1):
        """Builds a csv-formatted row containing the simulation's information.
        Then appends that to the current day's results file.

        The row is of the format
        '{simulation_number}, {candidate name}, {votes won}, ... , Winner, {winner}, {state name}, {Winning party of state}, ...'

        :param candidates: a list of all candidates in an the election
        :param candidate_sums: a dict with each candidate's electoral vote count, if any
        :param winner: the winner of the election
        :param state_results: dict containing the winner of each state
        :param simulation_number: the number (ID) of the simulation, if any"""
        # Save the electoral college results
        today_date = date.today()
        row = str(simulation_number) + ', '
        for candidate in candidates:
            row += str(candidate) + ', '
            if candidate in candidate_sums.keys():
                row += str(candidate_sums[candidate]) + ', '
            else:
                row += ', '
        row += f'Winner, {winner}, '

        state_labels_list = []
        for state, candidate_winner in state_results.items():
            state_labels_list.append(str(state))
            #state_labels_list.append(str(candidate_winner))
            state_labels_list.append(candidate_winner.party)
        row += ', '.join(state_labels_list)
        row += '\n'

        with open(f'data/results/results{str(today_date)}.csv', 'a+') as f:
            f.write(row)

    def run_simulations(self, num_simulations: int, candidates: [Candidate], verbose=False) -> {Candidate: int}:
        """Runs the specified number of simulated elections, adds up the number of wins of each candidate, then uses
        that to approximate the probability of a win for each candidate.

        If verbose is specified, it prints each simulation to the console and to disk.

        :param num_simulations: the number of simulations to run
        :param candidates: list of all candidates in the election
        :param verbose: bool that if true, prints the results of each simulated election to console and disk
        :returns a dict containing the number of election wins for each candidate
        """
        candidate_win_counts = {candidate: 0 for candidate in candidates}
        candidate_win_counts[None] = 0  # Draws are totally feasible
        write_in_candidate = Candidate('Write-in', 'I')  # Voters can write-in, and sometimes they could win.
        candidate_win_counts[write_in_candidate] = 0

        with Pool(NUM_CPU) as pool:
            results = pool.starmap(self.each_iteration, [(i, candidates, verbose, write_in_candidate) for i in range(num_simulations)])
            for candidate_sums in results:
                candidate_win_counts[self.get_winner(candidate_sums)] += 1

        return candidate_win_counts

    def each_iteration(self, i, candidates, verbose, write_in_candidate):
        results = self.run_one_simulation(candidates)
        candidate_sums = self.analyze_simulation(results)
        if verbose:
            winner = self.get_winner(candidate_sums)
            print(f'Simulation {i}: ', candidate_sums, 'Winner:', winner)
            self.save_simulation_to_csv(candidates, candidate_sums, winner, results, i)
            if write_in_candidate in candidate_sums.keys():
                print(f'Independent won a state with {candidate_sums[write_in_candidate]} votes')
        return candidate_sums
