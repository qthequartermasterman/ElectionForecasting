from ElectoralCollege import ElectoralCollege
from Candidate import Candidate
from StateFunction import State

candidates_names = [('Jim', 'D'), ('Bob', 'R')]
candidates = [Candidate(*can) for can in candidates_names]

ec = ElectoralCollege()
winners = ec.run_one_simulation(candidates)
print(winners)
multiple_simulations = ec.run_simulations(10000, candidates)
print('Multiple Simulations')
print(multiple_simulations)