from dataclasses import dataclass


@dataclass(frozen=True)
class Party:
    name: str
    abbreviation: str


RepublicanParty = Party('Republican', 'R')
DemocratParty = Party('Democrat', 'D')
LibertarianParty = Party('Libertarian', 'L')
GreenParty = Party('Green', 'G')
WriteIn = Party('Write-in', 'W')
Independent = Party('Independent', 'I')
