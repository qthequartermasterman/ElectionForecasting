from unittest import TestCase
# from Candidate import Candidate
from ElectionForecasting.core.Candidate import Candidate
from ElectionForecasting.core.Party import DemocratParty, RepublicanParty


class TestCandidate(TestCase):
    def setUp(self) -> None:
        self.candidate = Candidate('Jim', DemocratParty)

    def test_repr(self):
        self.assertEqual(repr(self.candidate), 'Jim (D)')

    def test_eq(self):
        candidate1 = Candidate('Jim', DemocratParty)
        self.assertEqual(self.candidate, candidate1)

    def test_not_eq(self):
        candidate1 = Candidate('Jim', RepublicanParty)
        candidate2 = Candidate('Bob', DemocratParty)
        candidate3 = Candidate('Bob', RepublicanParty)
        self.assertNotEqual(self.candidate, candidate1)
        self.assertNotEqual(self.candidate, candidate2)
        self.assertNotEqual(self.candidate, candidate3)
