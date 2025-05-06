from cp2025.algorithms.Depersonalizator import Depersonalizator
from cp2025.utility.GeneralizationRange import GeneralizationRange
import numpy as np

class Shuffler(Depersonalizator):
    def __init__(self, columns_ids_to_shuffle = None, seed = None):
        super().__init__([0])
        self.columns_ids_to_shuffle = columns_ids_to_shuffle
        self.seed = seed

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if self.columns_ids_to_shuffle is None:
            self.columns_ids_to_shuffle = list(range(identifiers.shape[1] + quasi_identifiers.shape[1] + sensitives.shape[1]))

        if self.seed is not None:
            np.random.seed(self.seed)

        for i in self.columns_ids_to_shuffle:
            if i in self.identifiers_ids:
                col_to_shuffle_id = self.identifiers_ids.index(i)
                np.random.shuffle(identifiers[:, col_to_shuffle_id])
            elif i in self.quasi_identifiers_ids:
                col_to_shuffle_id = self.quasi_identifiers_ids.index(i)
                np.random.shuffle(quasi_identifiers[:, col_to_shuffle_id])
            elif i in self.sensitives_ids:
                col_to_shuffle_id = self.sensitives_ids.index(i)
                np.random.shuffle(sensitives[:, col_to_shuffle_id])

        return identifiers, quasi_identifiers

if __name__ == "__main__":
    df = [
        [1, GeneralizationRange(1, 2), "a", UnorderedClass(1), 1],
        [2, GeneralizationRange(1, 3), "b", UnorderedClass(2), 2],
        [3, GeneralizationRange(1, 4), "c", UnorderedClass(3), 3],
        [4, GeneralizationRange(1, 5), "d", UnorderedClass(4), 4],
    ]
    df_shuffled = Shuffler(columns_ids_to_shuffle=[1, 2, 3, 4], seed=0).depersonalize(df, identifiers_ids=[0, 1], sensitives_ids=[4])[0]
    for row in df_shuffled:
        print(*row)

