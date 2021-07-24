import random
from collections import defaultdict
from typing import Tuple, List, Dict, Union
import asyncio

from .Candidate import Candidate, TokenEnsemble
from .ElectionRace import ElectionRace, ElectionResult
from .Party import DemocratParty, RepublicanParty, Party
from .PollingData import PollingData
from .State import States, State, ElectoralCollegeVotingMethod, total_electoral_votes

HouseDistrict = Tuple[States, int, ElectionRace]


def dict_sum(a, b):
    """Adds together the values of matching keys of two dictionaries.
    :param a: first dict to add
    :param b: second dict to add

    :returns dictionary with added values for duplicate keys and the value of singular keys"""
    temp = {
        a_key: a[a_key] + b[a_key] if a_key in b.keys() else a[a_key]
        for a_key in a.keys()
    }

    for b_key in b.keys():
        if b_key not in a.keys():
            temp[b_key] = b[b_key]
    return temp


def determine_winner(election_result: ElectionResult) -> Candidate:
    return max(election_result, key=election_result.get)  # Pick the winner


class NationalElection:
    """
    Contains the functionality to to simulate an election in every Congressional District in the United States.

    By simulating by congressional district, simulations can simulate house, senate, and electoral college elections
    at once.

    For now, this assumes that every voter votes one-party down-ballot, which is not a 100% reasonable assumption.

    TODO: Implement more granular level voting.

    """

    def __init__(self, polling_data=None):
        """

        :param polling_data: a polling data instance.
        """
        self.polling_data = polling_data or PollingData()
        self.districts: List[HouseDistrict] = self._init_congressional_districts()
        self.num_representatives = 435  # Set constant by the Reapportionment Act of 1929
        self.num_senators = 100  # Set as 2*num_states by the Constitution. This is constant enough for our purposes.
        self.house: Dict[States, Dict[int, Candidate]] = defaultdict(lambda: {})
        self.senate: Dict[States, List[Candidate]] = defaultdict(lambda: [])
        self.president: Candidate = None
        self.vice_president: Candidate = None

    def _init_congressional_districts(self) -> List[HouseDistrict]:
        """
        Instantiate all of the ElectionRace objects we will need.
        :return: List of tuples representing the state, district number, and an ElectionRace number for that race.
        """
        districts = []
        for state in States:
            for i in range(1, state.value.num_representatives + 1):
                # TODO: instantiate with correct population
                districts.append((state, i, ElectionRace(name=f'{state.value.abbreviation}-{i}',
                                                         polling_data=self.polling_data)))
        # D.C. doesn't have any congressional districts, but we still need it for presidential elections.
        districts.append((States.DistrictOfColumbia, 0, ElectionRace('DC-0', polling_data=self.polling_data)))
        return districts

    async def run_one_simulation(self, candidates: List[Candidate],
                                 verbose=True) -> Dict[HouseDistrict, ElectionResult]:
        """
        Runs a single national election simulation. For each state, it generates a single winner
        :param verbose:
        :param candidates: a list of candidates
        :returns a dictionary with house districts as keys and the election results as values"""
        return {race: race[2].get_winner(candidates) for race in self.districts}

    async def run_election(self, candidates: List[Candidate] = TokenEnsemble, verbose=True):
        # TODO: Implement non-down-ballot voting
        # Run the House election
        district_results: Dict[HouseDistrict, ElectionResult] = await self.run_one_simulation(candidates, verbose)
        house = self.determine_house(district_results, verbose)
        # Run the Senate election
        senate = self.determine_senate(district_results, verbose)
        # Run the Presidential Election
        electoral_college = await self.determine_electoral_college(district_results, verbose)
        president, vice_president = self.determine_present_vice_president(electoral_college, verbose)

    async def determine_house(self, district_results: Dict[HouseDistrict, ElectionResult],
                              verbose=True) -> Dict[States, Dict[int, Candidate]]:
        """

        TODO: do run-off elections in districts that do not have a majority winner
        :param verbose:
        :param district_results:
        :return:
        """
        house: Dict[States, Dict[int, Candidate]] = defaultdict(lambda: {})
        for district, result in district_results.items():
            state = district[0]
            if state != States.DistrictOfColumbia:
                district_number = district[1]
                winner = determine_winner(result)
                house[state][district_number] = winner
        self.house = house
        return house

    async def determine_senate(self, district_results: Dict[HouseDistrict, ElectionResult],
                               verbose=True) -> Dict[States, List[Candidate]]:
        """
        TODO: implement run-off elections.
        TODO: implement multiple senate elections in one state (see Georgia 2020)
        :param verbose:
        :param district_results:
        :return:
        """
        senate: Dict[States, List[Candidate]] = defaultdict(lambda: [])
        state_candidate_count: Dict[States, Dict[Candidate, int]] = defaultdict(lambda: defaultdict(lambda: 0))
        districts_won: Dict[States, List[Candidate]] = defaultdict(lambda: [])
        for district, result in district_results.items():
            state = district[0]
            if len(state.value.senators) < 2:
                state_candidate_count[state] = dict_sum(state_candidate_count[state], result)
                districts_won[state].append(determine_winner(result))
        # TODO: figure out this logic
        for state in States:
            senate[state].extend(state.value.senators)
        for state, candidate_count in state_candidate_count.items():
            if state != States.DistrictOfColumbia and len(state.value.senators) < 2:
                senate[state].extend([determine_winner(candidate_count) for _ in range(2-len(senate[state]))])
        self.senate = senate
        return senate

    async def determine_electoral_college(self, district_results: Dict[HouseDistrict, ElectionResult],
                                          verbose=True) -> Dict[Candidate, int]:
        """

        :param verbose:
        :param district_results:
        :return:
        """
        # Dictionary with each candidates electoral college total. Defaults to 0 for readability
        electoral_sums: Dict[Candidate, int] = defaultdict(lambda: 0)
        state_candidate_count: Dict[States, Dict[Candidate, int]] = defaultdict(lambda: defaultdict(lambda: 0))
        districts_won: Dict[States, List[Candidate]] = defaultdict(lambda: [])
        for district, result in district_results.items():
            state = district[0]
            state_candidate_count[state] = dict_sum(state_candidate_count[state], result)
            districts_won[state].append(determine_winner(result))

        for state, candidate_count in state_candidate_count.items():
            # state is originally the States enum, but for convenience, grab the State object
            state_object: State = state.value
            winner = determine_winner(candidate_count)
            if verbose and winner.party not in [DemocratParty, RepublicanParty]:
                print(f'\t{winner} won {state}, with {state_object.electoral_votes} electoral votes.')

            if state_object.electoral_vote_method == ElectoralCollegeVotingMethod.WinnerTakesAll:
                # In a Winner-Take-All state, the popular vote determines who gets all votes.
                electoral_sums[winner] += state_object.electoral_votes
            elif state_object.electoral_vote_method == ElectoralCollegeVotingMethod.CongressionalDistrictMethod:
                # In a Congressional District Method state, every house district gets one, then the popular vote
                # determines the two votes extra electoral votes.
                electoral_sums[winner] += 2
                for candidate in districts_won[state]:
                    electoral_sums[candidate] += 1
        return electoral_sums

    async def determine_present_vice_president(self, electoral_college_counts: ElectionResult,
                                               verbose=True) -> Tuple[Candidate, Candidate]:
        """
        Determine the President-Elect of the United States. Normally, this is determined by a simple majority of
        electoral college votes.

        In the event, however, of no majority in the electoral college, the presidential race immediately
        goes to the House of Representatives, where each state (not including DC) gets a single vote.
        :param verbose:
        :param electoral_college_counts:
        :return:
        """
        # Count the electoral college
        for candidate, electoral_votes in electoral_college_counts.items():
            if electoral_votes > total_electoral_votes / 2:
                return candidate, candidate

        # Only the top three candidates go onto contingency elections
        top_three_candidates = sorted(electoral_college_counts, key=electoral_college_counts.get, reverse=True)[:3]

        # Contingency election in the House (POTUS)
        president: Candidate = None
        for state, representatives in self.house.items():
            party_affiliations = [representative.party for representative in representatives.values()]
            majority_party = max(set(party_affiliations),
                                 key=party_affiliations.count)  # party with most reps in a state
            for candidate in top_three_candidates:
                # Generally state blocs will vote for the candidate with the majority party in that state delegation
                if candidate.party == majority_party:
                    president = candidate
                    break
            if president is None:
                # If no candidate has the same party as the majority delegate party, pick one at random for
                # this simulation
                president = random.choice(top_three_candidates)

        # Contingency election in the Senate (VPOTUS)
        vice_president: Candidate = president
        # TODO: implement senate and VP contingent election

        self.president, self.vice_president = president, vice_president
        return president, vice_president

    @property
    def house_party_breakdown(self) -> Dict[Party, int]:
        """

        :return:
        """
        parties = defaultdict(lambda: 0)
        for districts in self.house.values():
            for representative in districts.values():
                parties[representative.party] += 1
        return dict(parties)

    @property
    def house_majority(self) -> Union[Party, None]:
        """Simple majority of representative party in the House. Returns None if no majority"""
        for party, count in self.house_party_breakdown.items():
            if count > self.num_representatives / 2:
                return party
        return None

    @property
    def senate_party_breakdown(self) -> Dict[Party, int]:
        """

        :return:
        """
        parties = defaultdict(lambda: 0)
        for senators in self.senate.values():
            for senator in senators:
                parties[senator.party] += 1
        return dict(parties)

    @property
    def senate_majority(self) -> Union[Party, None]:
        """Simple majority of senator parties, unless there is a tie. In which case, VP is tiebreaker"""
        parties = self.senate_party_breakdown
        top_two_parties = sorted(parties, key=parties.get, reverse=True)[:2]
        if parties[top_two_parties[0]] > self.num_senators / 2:
            # If the top party has a clear majority, return it
            return top_two_parties[0]
        # If the two parties are tied, the president will act as a tiebreaker for his party
        if self.vice_president is not None:
            for party in top_two_parties:
                if party == self.vice_president.party:
                    return party
        return None
