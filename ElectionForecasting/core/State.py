from dataclasses import dataclass
from enum import Enum, auto
from .Party import RepublicanParty, DemocratParty
from typing import List, Tuple, FrozenSet
from .Candidate import Candidate


class ElectoralCollegeVotingMethod(Enum):
    WinnerTakesAll = auto()  # Whoever wins the state popular vote takes all the votes.
    CongressionalDistrictMethod = auto()


@dataclass(frozen=True)
class State:
    """
    Contains all of the relevant electoral college data for a state.

    Note: 'State' in this context refers to any state or region that holds electoral votes.
    This includes all 50 states, the District of Columbia, and the congressional districts in Maine and Nebraska."""
    abbreviation: str
    name: str
    num_representatives: int
    num_senators: int = 2  # Set constant by the constitution. D.C. does not get senators.
    num_extra_electoral_votes: int = 0  # D.C. gets 3 electoral votes unrelated to senators or representatives.
    electoral_vote_method: ElectoralCollegeVotingMethod = ElectoralCollegeVotingMethod.WinnerTakesAll
    senators: FrozenSet[Candidate] = frozenset()

    @property
    def electoral_votes(self):
        return self.num_representatives + self.num_senators + self.num_extra_electoral_votes

    def __repr__(self):
        return f'{self.name} ({self.abbreviation})'


class States(Enum):
    Alabama: State = State('AL', 'Alabama', 7, senators=frozenset([Candidate('Tommy Tuberville', RepublicanParty), ]))
    Alaska: State = State('AK', 'Alaska', 1, senators=frozenset([Candidate('Dan Sullivan', RepublicanParty), ]))
    Arizona: State = State('AZ', 'Arizona', 9, senators=frozenset([Candidate('Kyrsten Sinema', DemocratParty), ]))
    Arkansas: State = State('AR', 'Arkansas', 4, senators=frozenset([Candidate('Tom Cotton', RepublicanParty), ]))
    California: State = State('CA', 'California', 53,
                              senators=frozenset([Candidate('Dianne Feinstein', DemocratParty), ]))
    Colorado: State = State('CO', 'Colorado', 7, senators=frozenset([Candidate('John Hickenlooper', DemocratParty), ]))
    Connecticut: State = State('CT', 'Connecticut', 5, senators=frozenset([Candidate('Chris Murphy', DemocratParty), ]))
    Delaware: State = State('DE', 'Delaware', 1, senators=frozenset(
        [Candidate('Tom Carper', DemocratParty), Candidate('Chris Coons', DemocratParty), ]))
    Florida: State = State('FL', 'Florida', 27, senators=frozenset([Candidate('Rick Scott', RepublicanParty), ]))
    Georgia: State = State('GA', 'Georgia', 14, senators=frozenset([Candidate('Jon Ossoff', DemocratParty), ]))
    Hawaii: State = State('HI', 'Hawaii', 2, senators=frozenset([Candidate('Mazie Hirono', DemocratParty), ]))
    Idaho: State = State('ID', 'Idaho', 2, senators=frozenset([Candidate('Jim Risch', RepublicanParty), ]))
    Illinois: State = State('IL', 'Illinois', 18, senators=frozenset([Candidate('Dick Durbin', DemocratParty), ]))
    Indiana: State = State('IN', 'Indiana', 9, senators=frozenset([Candidate('Mike Braun', RepublicanParty), ]))
    Iowa: State = State('IA', 'Iowa', 4, senators=frozenset([Candidate('Joni Ernst', RepublicanParty), ]))
    Kansas: State = State('KS', 'Kansas', 4, senators=frozenset([Candidate('Roger Marshall', RepublicanParty), ]))
    Kentucky: State = State('KY', 'Kentucky', 6, senators=frozenset([Candidate('Mitch McConnell', RepublicanParty), ]))
    Louisiana: State = State('LA', 'Louisiana', 6, senators=frozenset([Candidate('Bill Cassidy', RepublicanParty), ]))
    Maine: State = State('ME', 'Maine', 2,
                         electoral_vote_method=ElectoralCollegeVotingMethod.CongressionalDistrictMethod,
                         senators=frozenset(
                             [Candidate('Angus King', DemocratParty), Candidate('Susan Collins', RepublicanParty), ]))
    Maryland: State = State('MD', 'Maryland', 8, senators=frozenset([Candidate('Ben Cardin', DemocratParty), ]))
    Massachusetts: State = State('MA', 'Massachusetts', 9, senators=frozenset(
        [Candidate('Elizabeth Warren', DemocratParty), Candidate('Ed Markey', DemocratParty), ]))
    Michigan: State = State('MI', 'Michigan', 14, senators=frozenset(
        [Candidate('Debbie Stabenow', DemocratParty), Candidate('Gary Peters', DemocratParty), ]))
    Minnesota: State = State('MN', 'Minnesota', 8, senators=frozenset(
        [Candidate('Amy Klobuchar', DemocratParty), Candidate('Tina Smith', DemocratParty), ]))
    Mississippi: State = State('MS', 'Mississippi', 4, senators=frozenset(
        [Candidate('Roger Wicker', RepublicanParty), Candidate('Cindy Hyde-Smith', RepublicanParty), ]))
    Missouri: State = State('MO', 'Missouri', 8, senators=frozenset([Candidate('Josh Hawley', RepublicanParty), ]))
    Montana: State = State('MT', 'Montana', 1, senators=frozenset(
        [Candidate('Jon Tester', DemocratParty), Candidate('Steve Daines', RepublicanParty), ]))
    Nebraska: State = State('NE', 'Nebraska', 3,
                            electoral_vote_method=ElectoralCollegeVotingMethod.CongressionalDistrictMethod,
                            senators=frozenset(
                                [Candidate('Deb Fischer', RepublicanParty), Candidate('Ben Sasse', RepublicanParty), ]))
    Nevada: State = State('NV', 'Nevada', 4, senators=frozenset([Candidate('Jacky Rosen', DemocratParty), ]))
    NewHampshire: State = State('NH', 'New Hampshire', 2,
                                senators=frozenset([Candidate('Jeanne Shaheen', DemocratParty), ]))
    NewJersey: State = State('NJ', 'New Jersey', 12, senators=frozenset(
        [Candidate('Bob Menendez', DemocratParty), Candidate('Cory Booker', DemocratParty), ]))
    NewMexico: State = State('NM', 'New Mexico', 3, senators=frozenset(
        [Candidate('Martin Heinrich', DemocratParty), Candidate('Ben Ray Luján', DemocratParty), ]))
    NewYork: State = State('NY', 'New York', 27, senators=frozenset([Candidate('Kirsten Gillibrand', DemocratParty), ]))
    NorthCarolina: State = State('NC', 'North Carolina', 13,
                                 senators=frozenset([Candidate('Thom Tillis', RepublicanParty), ]))
    NorthDakota: State = State('ND', 'North Dakota', 1,
                               senators=frozenset([Candidate('Kevin Cramer', RepublicanParty), ]))
    Ohio: State = State('OH', 'Ohio', 16, senators=frozenset([Candidate('Sherrod Brown', DemocratParty), ]))
    Oklahoma: State = State('OK', 'Oklahoma', 5, senators=frozenset([Candidate('Jim Inhofe', RepublicanParty), ]))
    Oregon: State = State('OR', 'Oregon', 5, senators=frozenset([Candidate('Jeff Merkley', DemocratParty), ]))
    Pennsylvania: State = State('PA', 'Pennsylvania', 18,
                                senators=frozenset([Candidate('Bob Casey Jr.', DemocratParty), ]))
    RhodeIsland: State = State('RI', 'Rhode Island', 2, senators=frozenset(
        [Candidate('Sheldon Whitehouse', DemocratParty), Candidate('Jack Reed', DemocratParty), ]))
    SouthCarolina: State = State('SC', 'South Carolina', 7,
                                 senators=frozenset([Candidate('Lindsey Graham', RepublicanParty), ]))
    SouthDakota: State = State('SD', 'South Dakota', 1,
                               senators=frozenset([Candidate('Mike Rounds', RepublicanParty), ]))
    Tennessee: State = State('TN', 'Tennessee', 9, senators=frozenset(
        [Candidate('Marsha Blackburn', RepublicanParty), Candidate('Bill Hagerty', RepublicanParty), ]))
    Texas: State = State('TX', 'Texas', 36, senators=frozenset(
        [Candidate('Ted Cruz', RepublicanParty), Candidate('John Cornyn', RepublicanParty), ]))
    Utah: State = State('UT', 'Utah', 4, senators=frozenset([Candidate('Mitt Romney', RepublicanParty), ]))
    Vermont: State = State('VT', 'Vermont', 1, senators=frozenset([Candidate('Bernie Sanders', DemocratParty), ]))
    Virginia: State = State('VA', 'Virginia', 11, senators=frozenset(
        [Candidate('Tim Kaine', DemocratParty), Candidate('Mark Warner', DemocratParty), ]))
    Washington: State = State('WA', 'Washington', 10,
                              senators=frozenset([Candidate('Maria Cantwell', DemocratParty), ]))
    WestVirginia: State = State('WV', 'West Virginia', 3, senators=frozenset(
        [Candidate('Joe Manchin', DemocratParty), Candidate('Shelley Moore Capito', RepublicanParty), ]))
    Wisconsin: State = State('WI', 'Wisconsin', 8, senators=frozenset([Candidate('Tammy Baldwin', DemocratParty), ]))
    Wyoming: State = State('WY', 'Wyoming', 1, senators=frozenset(
        [Candidate('John Barrasso', RepublicanParty), Candidate('Cynthia Lummis', RepublicanParty), ]))
    DistrictOfColumbia: State = State('DC', 'District of Columbia', 0, 0, 3)


state_by_abbreviation = {state.value.abbreviation: state for state in States}
state_by_name = {state.value.name: state for state in States}

total_electoral_votes = sum([state.value.electoral_votes for state in States])

list_of_battleground_state_names = [States.Florida,
                                    States.Pennsylvania,
                                    States.Wisconsin,
                                    States.NorthCarolina,
                                    States.Michigan,
                                    States.Ohio,
                                    States.Minnesota,
                                    States.Iowa,
                                    States.Arizona,
                                    States.Nevada,
                                    States.Texas,
                                    States.Georgia,
                                    States.Virginia,
                                    States.NewHampshire,
                                    States.Maine,
                                    States.Colorado,
                                    States.NewMexico]
