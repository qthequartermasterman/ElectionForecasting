from unittest import TestCase
from ElectoralCollege import ElectoralCollege
from Candidate import Candidate


class TestElectoralCollege(TestCase):
    def setUp(self):
        self.ec = ElectoralCollege()

    def test_analyze_simulation(self):
        c1 = Candidate('Jim', 'D')
        c2 = Candidate('Bob', 'R')
        results = {'Alabama': c1,
                   'California': c2,
                   'Colorado': c1}
        analysis = self.ec.analyze_simulation(results)
        self.assertEqual(analysis, {c1: 18, c2: 55})
        results = {'Alabama': c1,
                   'California': c2,
                   'Colorado': c1,
                   'District of Columbia': c2}
        analysis = self.ec.analyze_simulation(results)
        self.assertEqual(analysis, {c1: 18, c2: 58})
