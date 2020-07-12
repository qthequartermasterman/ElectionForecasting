class Candidate:
    """Contains all the information to identify a candidate in analyses."""
    def __init__(self, name: str, party: str):
        self.name = name
        self.party = party

    def __repr__(self):
        return f'{self.name} ({self.party})'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(repr(self))
