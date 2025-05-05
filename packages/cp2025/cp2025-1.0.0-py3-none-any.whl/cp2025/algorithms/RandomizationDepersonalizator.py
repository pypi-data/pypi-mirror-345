from collections.abc import Iterable
import numpy as np
import random
import bisect
from cp2025.algorithms.Depersonalizator import Depersonalizator

class RandomOrdered:
    def __init__(self, sorted_values, values_type = 'ordered', scale = 0.25):
        self.sorted_values = sorted_values
        self.scale = scale
        self.values_type = values_type

    def __call__(self, x):
        pos_left = bisect.bisect_left(self.sorted_values, x)
        pos = pos_left
        if self.values_type == 'ordered':
            shift = int(np.random.normal(0, 1, 1)[0] * len(self.sorted_values) * self.scale)
            new_pos = pos + shift
            if new_pos < 0:
                new_pos = 0
            if new_pos >= len(self.sorted_values):
                new_pos = len(self.sorted_values) - 1
            return self.sorted_values[new_pos]
        else:
            shift = np.random.normal(0, 1, 1)[0] * len(self.sorted_values) * self.scale
            new_pos = pos + shift
            if new_pos < 0:
                return self.sorted_values[0]
            elif new_pos >= len(self.sorted_values):
                return self.sorted_values[-1]
            else:
                int_pos = int(new_pos)
                fractional_part = new_pos - int(new_pos)
                if int_pos == len(self.sorted_values) - 1:
                    return self.sorted_values[int_pos]
                return self.sorted_values[int_pos] + fractional_part * (self.sorted_values[int_pos + 1] - self.sorted_values[int_pos])

class RandomUnordered:
    def __init__(self, values):
        self.values = values

    def __call__(self, x):
        return x if random.choice([0,1]) == 0 else (random.choice(self.values))

class RandomizationBaselineDepersonalizator(Depersonalizator):
    def __init__(self, *, min_rand = None, max_rand = None, seed = None, rand_add = None, quasi_identifiers_types = None, scale = 1):
        super().__init__([0])
        self.min_rand = min_rand
        self.max_rand = max_rand
        self.seed = seed
        self.rand_add = rand_add
        self.quasi_identifiers_types = quasi_identifiers_types
        self.scale = scale

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers

        if self.seed is not None:
            random.seed(self.seed)

        if self.rand_add is None:
            self.rand_add = [None] * len(quasi_identifiers[0])
        else:
            self.rand_add = self.rand_add.copy()

        if self.quasi_identifiers_types is None:
            self.quasi_identifiers_types = ['unordered'] * len(quasi_identifiers[0])

        if not isinstance(self.min_rand, Iterable):
            self.min_rand = [self.min_rand] * len(quasi_identifiers[0])
        if not isinstance(self.max_rand, Iterable):
            self.max_rand = [self.max_rand] * len(quasi_identifiers[0])


        for i in range(len(self.rand_add)):
            if self.rand_add[i] is None:
                if self.quasi_identifiers_types[i] == 'real':
                    hist, bin_edges = np.histogram(quasi_identifiers[:, i].astype(float), bins=30, density=True)
                    new_values = np.random.choice(bin_edges[:-1], size=len(quasi_identifiers[:, i]), p=hist * np.diff(bin_edges))
                    self.rand_add[i] = RandomOrdered(np.sort(new_values), scale = self.scale, values_type='real')
                elif self.quasi_identifiers_types[i] == 'unordered':
                    self.rand_add[i] = RandomUnordered(quasi_identifiers[:, i].tolist())
                elif self.quasi_identifiers_types[i] == 'ordered':
                    values = sorted(quasi_identifiers[:, i].tolist())
                    self.rand_add[i] = RandomOrdered(values, scale = self.scale, values_type='ordered')

        for i in range(len(quasi_identifiers)):
            for j in range(len(quasi_identifiers[0])):
                quasi_identifiers[i][j] = self.rand_add[j](quasi_identifiers[i][j])

        return None, quasi_identifiers

if __name__ == '__main__':
    df = [
        [1, 1000, 0.1],
        [0, 0, 0],
        [3, 3000, 0.3],
        [5, 5000, 0.5],
    ]
    print(RandomizationBaselineDepersonalizator(quasi_identifiers_types=['real']*3, scale = 1).depersonalize(df))
