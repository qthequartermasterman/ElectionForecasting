from Candidate import Candidate
from ElectoralCollege import ElectoralCollege
from PollingData import PollingData

candidates_names = [('Joseph R. Biden Jr.', 'D', 'Biden'), ('Donald Trump', 'R', 'Trump'),
                    ('Jo Jorgensen', 'L', 'Jorgensen'), ('Howie Hawkins', 'G', 'Hawkins')]
candidates = [Candidate(*can) for can in candidates_names]

num_simulations = 20000
pd = PollingData()

ec = ElectoralCollege(pd)
multiple_simulations = ec.run_simulations(num_simulations, candidates, verbose=True)
print()
print(f'{num_simulations} Simulations with Polling Data')
print('Raw data:', multiple_simulations)
print('Probability:', {key: f'{round(100*value / num_simulations, 2)}%' for key, value in multiple_simulations.items()})
