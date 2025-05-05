import numpy as np

def join_unordered(lhs, rhs):
    if lhs == rhs:
        return lhs
    if isinstance(lhs, GeneralizationRange):
        arr1 = lhs.values_set
    else:
        arr1 = np.array([lhs])
    if isinstance(rhs, GeneralizationRange):
        arr2 = rhs.values_set
    else:
        arr2 = np.array([rhs])
    return GeneralizationRange(None, None, 'unordered', np.concatenate((arr1, arr2)))

def join_ordered(lhs, rhs, column_type):
    if lhs == rhs:
        return lhs
    if isinstance(lhs, GeneralizationRange):
        min1 = lhs.min
        max1 = lhs.max
    else:
        min1 = lhs
        max1 = lhs
    if isinstance(rhs, GeneralizationRange):
        min2 = rhs.min
        max2 = rhs.max
    else:
        min2 = rhs
        max2 = rhs
    return GeneralizationRange(min(min1, min2), max(max1, max2), column_type, None)


class GeneralizationRange:
    def __init__(self, mn=None, mx=None, column_type='ordered', column_values=None):
        self.column_type = column_type
        if column_type == 'real' or column_type == 'ordered':
            self.min = mn
            self.max = mx
        else:
            self.min = None
            self.max = None
        if column_type == 'unordered':
            self.values_set = list(set(column_values.tolist()))
        else:
            self.values_set = None

    def __repr__(self):
        if self.column_type == 'real' or self.column_type == 'ordered':
            return "[" + str(self.min) + ", " + str(self.max) + "]"
        if self.column_type == 'unordered':
            return str(self.values_set)
        return 'Incorrect column type'

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, GeneralizationRange):
            return False
        if self.column_type == 'real' or self.column_type == 'ordered':
            return self.min == other.min and self.max == other.max
        if self.column_type == 'unordered':
            return set(self.values_set) == set(other.values_set)
        return False

    def __ne__(self, other):
        if other is None:
            return False
        return not self.__eq__(other)

    def __lt__(self, other):
        if other is None:
            return False
        if self.column_type == 'real' or self.column_type == 'ordered':
            if isinstance(other, GeneralizationRange):
                return self.min < other.min
            else:
                return self.max < other
        else:
            return False

    def __gt__(self, other):
        if other is None:
            return False
        return not self.__eq__(other) and not self.__lt__(other)

    def __le__(self, other):
        if other is None:
            return False
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        if other is None:
            return False
        return self.__gt__(other) or self.__eq__(other)

    def __hash__(self):
        if self.column_type == 'real' or self.column_type == 'ordered':
            return hash((self.min, self.max))
        else:
            return hash(tuple(self.values_set))



