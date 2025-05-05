from cp2025.algorithms.Depersonalizator import Depersonalizator
import numpy as np

class ShufflerInBatches(Depersonalizator):
    def __init__(self, columns_ids_to_shuffle = None, seed = None):
        super().__init__([0])
        self.columns_ids_to_shuffle = columns_ids_to_shuffle
        self.seed = seed

    def get_batches(self, quasi_identifiers):
        rows2ids = dict()
        for i in range(quasi_identifiers.shape[0]):
            if tuple(quasi_identifiers[i].tolist()) in rows2ids:
                rows2ids[tuple(quasi_identifiers[i].tolist())].append(i)
            else:
                rows2ids[tuple(quasi_identifiers[i].tolist())] = [i]
        batches = []
        for key in rows2ids:
            batches.append(rows2ids[key])
        return batches

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if self.columns_ids_to_shuffle is None:
            self.columns_ids_to_shuffle = list(range(identifiers.shape[1] + quasi_identifiers.shape[1] + sensitives.shape[1]))

        if self.seed is not None:
            np.random.seed(self.seed)

        batches = self.get_batches(quasi_identifiers)

        for batch in batches:
            for i in self.columns_ids_to_shuffle:
                if i in self.identifiers_ids:
                    col_to_shuffle_id = self.identifiers_ids.index(i)
                    np.random.shuffle(identifiers[batch, col_to_shuffle_id])
                elif i in self.quasi_identifiers_ids:
                    col_to_shuffle_id = self.quasi_identifiers_ids.index(i)
                    np.random.shuffle(quasi_identifiers[batch, col_to_shuffle_id])
                elif i in self.sensitives_ids:
                    col_to_shuffle_id = self.sensitives_ids.index(i)
                    np.random.shuffle(sensitives[batch, col_to_shuffle_id])

        return identifiers, quasi_identifiers


