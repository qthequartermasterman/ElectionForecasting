from ElectoralCollege import ElectoralCollege
from Candidate import Candidate
from StateFunction import State
from PollingData import PollingData

candidates_names = [('Joseph R. Biden Jr.', 'D', 'Biden'), ('Donald Trump', 'R', 'Trump')]
candidates = [Candidate(*can) for can in candidates_names]

num_simulations = 20000
pd = PollingData()

ec = ElectoralCollege(pd)
multiple_simulations = ec.run_simulations(num_simulations, candidates, verbose=True)
print()
print(f'{num_simulations} Simulations with Polling Data')
print('Raw data:', multiple_simulations)
print('Probability:', {key: value/num_simulations for key, value in multiple_simulations.items()})