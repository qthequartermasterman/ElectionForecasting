from ElectionForecasting.core.Candidate import Candidate
from ElectionForecasting.core.ElectionSimulator import ElectionSimulator
from ElectionForecasting.core.PollingData import PollingData
from ElectionForecasting.core.Party import DemocratParty, RepublicanParty, LibertarianParty, GreenParty

import asyncio


async def main():
    print('starting')
    candidates_names = [('Joseph R. Biden Jr.', DemocratParty, 'Biden'), ('Donald Trump', RepublicanParty, 'Trump'),
                        ('Jo Jorgensen', LibertarianParty, 'Jorgensen'), ('Howie Hawkins', GreenParty, 'Hawkins')]
    candidates = [Candidate(*can) for can in candidates_names]
    print('finished candidates')

    num_simulations = 200 #20000
    pd = PollingData()
    print('finished pollingdata')

    ec = ElectionSimulator(pd)
    print('finished election simulator')
    multiple_simulations = await ec.run_simulations(num_simulations, candidates, verbose=True)
    totals = await ec.calculate_probabilities(multiple_simulations)
    presidents, vice_presidents, house_majorities, senate_majorities = totals
    print()
    print(f'{num_simulations} Simulations with Polling Data')
    #print('Raw data:', totals)
    print('Presidents:', {key: f'{round(100 * value / num_simulations, 2)}%' for key, value in presidents.items()})
    print('Vice Presidents:', {key: f'{round(100 * value / num_simulations, 2)}%' for key, value in vice_presidents.items()})
    print('House Majority:', {key: f'{round(100 * value / num_simulations, 2)}%' for key, value in house_majorities.items()})
    print('Senate Majority:', {key: f'{round(100 * value / num_simulations, 2)}%' for key, value in senate_majorities.items()})
    # print('Probability:', {key: f'{round(100 * value / num_simulations, 2)}%' for key, value in presidents.items()})


if __name__ == '__main__':
    asyncio.run(main())
