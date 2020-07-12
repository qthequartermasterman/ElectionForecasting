from unittest import TestCase
from Candidate import Candidate


class TestCandidate(TestCase):
    def setUp(self) -> None:
        self.candidate = Candidate('Jim', 'D')


class TestRepr(TestCandidate):
    def test_repr(self):
        self.assertEqual(repr(self.candidate), 'Jim (D)')


class TestEq(TestCandidate):
    def test_eq(self):
        candidate1 = Candidate('Jim', 'D')
        self.assertEqual(self.candidate, candidate1)

    def test_not_eq(self):
        candidate1 = Candidate('Jim', 'R')
        candidate2 = Candidate('Bob', 'D')
        candidate3 = Candidate('Bob', 'R')
        self.assertNotEqual(self.candidate, candidate1)
        self.assertNotEqual(self.candidate, candidate2)
        self.assertNotEqual(self.candidate, candidate3)