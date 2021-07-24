from unittest import TestCase
from ElectionForecasting.core.Party import *


class TestParty(TestCase):
    def test_builtin_parties(self):
        parties = {RepublicanParty: ('Republican', 'R'),
                   DemocratParty: ('Democrat', 'D'),
                   LibertarianParty: ('Libertarian', 'L'),
                   GreenParty: ('Green', 'G'), WriteIn: ('Write-in', 'W'),
                   Independent: ('Independent', 'I')}

        for party, names in parties.items():
            self.assertEqual(names[0], party.name)
            self.assertEqual(names[1], party.abbreviation)
