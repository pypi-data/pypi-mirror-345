from cp2025.algorithms.Depersonalizator import Depersonalizator
import numpy as np
import hashlib


class IdentifierHasher(Depersonalizator):
    def __init__(self):
        super().__init__([])

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        hashed_identifiers = np.copy(identifiers)
        for i in range(hashed_identifiers.shape[0]):
            for j in range(hashed_identifiers.shape[1]):
                hashed_identifiers[i, j] = hashlib.sha256(str(identifiers[i]).encode()).hexdigest()
        return hashed_identifiers, quasi_identifiers

