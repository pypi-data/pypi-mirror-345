class UnorderedClass:
    def __init__(self, v):
        self.v = v

    def __hash__(self):
        return self.v

    def __eq__(self, other):
        if not isinstance(other, UnorderedClass):
            return False
        return self.v == other.v

    def __repr__(self):
        return 'UnorderedClass({})'.format(self.v)