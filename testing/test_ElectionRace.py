from typing import Dict
from unittest import TestCase, IsolatedAsyncioTestCase
from ElectionForecasting.core.ElectionRace import ElectionRace, ElectionType
from ElectionForecasting.core.Candidate import Candidate
from ElectionForecasting.core.Party import DemocratParty, RepublicanParty, WriteIn


class TestElectionRace(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.house_tx38 = ElectionRace('TX-38')
        self.house_al7 = ElectionRace('AL-7')
        self.candidates = [Candidate('Biden', DemocratParty), Candidate('Trump', RepublicanParty),
                           Candidate('Write-In', WriteIn)]

    async def test_get_winner_uniform_random(self):
        self.assertIn(await self.house_tx38.get_winner_random(self.candidates), self.candidates)
        self.assertIn(await self.house_tx38.get_winner(self.candidates,
                                                       simulation_type=ElectionType.UniformRandomDistribution),
                      self.candidates)
        self.assertIn(await self.house_al7.get_winner_random(self.candidates), self.candidates)
        self.assertIn(await self.house_al7.get_winner(self.candidates,
                                                      simulation_type=ElectionType.UniformRandomDistribution),
                      self.candidates)

    async def test_get_winner_given_polling_distribution(self):
        polling_distribution: Dict[Candidate, float] = dict(zip(self.candidates, [.67, .3, .01]))
        self.assertIn(await self.house_tx38.get_winner_with_distribution(polling_distribution), self.candidates)
        self.assertIn(await self.house_al7.get_winner_with_distribution(polling_distribution), self.candidates)

    async def test_get_winner_real_polling_distribution(self):
        self.assertIn(
            await self.house_tx38.get_winner(self.candidates, simulation_type=ElectionType.PollingDistribution),
            self.candidates)
        self.assertIn(
            await self.house_al7.get_winner(self.candidates, simulation_type=ElectionType.PollingDistribution),
            self.candidates)

    async def test_get_polling_distribution(self):
        poll_data = await self.house_tx38.get_polling_distribution(candidates=self.candidates)
        print(poll_data)
        self.assertEqual(poll_data[-1], 0)  # There is probably no candidate named 'Write-in'
        self.assertLess(sum(poll_data), 1)  # The polls cannot add up to more than 1
