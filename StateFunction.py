import random
from Candidate import Candidate


class State:
    def __init__(self, name: str):
        self.name = name

    def get_winner(self, candidates: [Candidate]) -> Candidate:
        return random.choice(candidates)
