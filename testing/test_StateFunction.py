from unittest import TestCase
from StateFunction import State
from Candidate import Candidate


class TestState(TestCase):
    def setUp(self) -> None:
        self.state = State('Texas')
        self.state1 = State('Alabama')
        self.candidates = [Candidate('Biden', 'D'), Candidate('Trump', 'R'), Candidate('Write-In', 'I')]
    def test_get_winner(self):
        pass

    def test_get_polling_distribution(self):
        poll_data = self.state.get_polling_distribution(candidates=self.candidates)
        print(poll_data)
        self.assertEqual(poll_data[-1], 0)  # There is probably no candidate named 'Write-in'
        self.assertLess(sum(poll_data), 1)  # The polls cannot add up to more than 1
