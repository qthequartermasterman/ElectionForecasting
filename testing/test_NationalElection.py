from ElectionForecasting.core.NationalElection import NationalElection
from ElectionForecasting.core.Candidate import Candidate
from ElectionForecasting.core.Party import DemocratParty, RepublicanParty, LibertarianParty
from ElectionForecasting.core.ElectionRace import ElectionRace
from ElectionForecasting.core.PollingData import PollingData
from unittest import TestCase, IsolatedAsyncioTestCase, skip

from ElectionForecasting.core.State import States


def house_district(state: States, number: int, polling_data: PollingData) -> (States, int, ElectionRace):
    return state, number, ElectionRace(f'{state.value.abbreviation}-{number}', polling_data=polling_data)


class TestNationalElection(IsolatedAsyncioTestCase):
    def test_init(self):
        election = NationalElection()
        self.assertEqual(436, len(election.districts))

    async def test_electoral_college(self):
        election = NationalElection()
        polling_data = PollingData()
        c1 = Candidate('Jim', DemocratParty)
        c2 = Candidate('Bob', RepublicanParty)
        results = {house_district(States.Alabama, 1, polling_data): {c1: 15, c2: 5},
                   house_district(States.California, 1, polling_data): {c1: 5, c2: 15},
                   house_district(States.Colorado, 1, polling_data): {c1: 15, c2: 5},
                   }
        analysis = await election.determine_electoral_college(results)
        self.assertEqual(analysis, {c1: 18, c2: 55})
        results = {house_district(States.Alabama, 1, polling_data): {c1: 15, c2: 5},
                   house_district(States.California, 1, polling_data): {c1: 5, c2: 15},
                   house_district(States.Colorado, 1, polling_data): {c1: 15, c2: 5},
                   house_district(States.DistrictOfColumbia, 0, polling_data): {c1: 1, c2: 5},
                   }
        analysis = await election.determine_electoral_college(results)
        self.assertEqual(analysis, {c1: 18, c2: 58})

    async def test_determine_president_electoral_college_win(self):
        """
        Test a normal electoral college win. No contingency election needed.
        In this test, 'Bob' will win all the electoral votes.
        """
        election = NationalElection()
        c1 = Candidate('Jim', DemocratParty)
        c2 = Candidate('Bob', RepublicanParty)
        results = {race: {c1: 10, c2: 300} for race in election.districts}
        analysis = await election.determine_electoral_college(results)
        president, vice_president = await election.determine_president_vice_president(analysis)
        self.assertEqual(c2, president)
        self.assertEqual(c2, vice_president)

    @skip('Test Not yet implemented')
    async def test_determine_president_contingency_election(self):
        """Contingency Election (i.e. Electoral college failed to win a simple majority)"""
        election = NationalElection()
        c1 = Candidate('Jim', DemocratParty)
        c2 = Candidate('Bob', RepublicanParty)
        c3 = Candidate('Fred', LibertarianParty)

    async def test_determine_house(self):
        election = NationalElection()
        c1 = Candidate('Jim', DemocratParty)
        c2 = Candidate('Bob', RepublicanParty)

        # Election where Candidate 'Bob' somehow wins every house district in the country.
        results = {race: {c1: 10, c2: 300} for race in election.districts}
        house = await election.determine_house(results)
        self.assertEqual({RepublicanParty: 435}, election.house_party_breakdown)
        self.assertEqual(RepublicanParty, election.house_majority)

        # Election where country is split evenly
        results = {race: {c1: 10, c2: 300} if i % 2 else {c1: 300, c2: 10} for i, race in enumerate(election.districts)}
        house = await election.determine_house(results)
        self.assertEqual({RepublicanParty: 217, DemocratParty: 218}, election.house_party_breakdown)
        self.assertEqual(DemocratParty, election.house_majority)

    async def test_determine_senate(self):
        election = NationalElection()
        c1 = Candidate('Jim', DemocratParty)
        c2 = Candidate('Bob', RepublicanParty)

        # Election where Candidate 'Bob' somehow wins every house district in the country.
        results = {race: {c1: 10, c2: 300} for race in election.districts}
        senate = await election.determine_senate(results)
        self.assertEqual({RepublicanParty: 64, DemocratParty: 36}, election.senate_party_breakdown)
        self.assertEqual(RepublicanParty, election.senate_majority)
