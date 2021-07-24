from dataclasses import dataclass

from .Party import Party, RepublicanParty, DemocratParty, LibertarianParty, GreenParty


@dataclass(eq=True, frozen=True)
class Candidate:
    """Contains all the information to identify a candidate in analyses."""

    name: str
    party: Party
    short_name: str = ''

    def __post_init__(self):
        # short circuit evaluation. If short_name is a falsy, then it uses the full name
        super().__setattr__('short_name', self.short_name or self.name)

    def __repr__(self):
        return f'{self.short_name} ({self.party.abbreviation})'


TokenRepublican = Candidate('Unnamed Republican', RepublicanParty, 'Republican')
TokenDemocrat = Candidate('Unnamed Democrat', DemocratParty, 'Democrat')
TokenLibertarian = Candidate('Unnamed Libertarian', LibertarianParty, 'Libertarian')
TokenGreen = Candidate('Unnamed Green', GreenParty, 'Green')
TokenEnsemble = [TokenRepublican, TokenDemocrat, TokenLibertarian, TokenGreen]
