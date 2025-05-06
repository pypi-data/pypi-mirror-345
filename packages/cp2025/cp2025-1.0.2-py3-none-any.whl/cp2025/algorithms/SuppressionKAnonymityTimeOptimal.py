from cp2025.algorithms.Depersonalizator import Depersonalizator
from cp2025.utility.diatances import dfs_hamming_distances
from cp2025.utility.groupping import group_by_dist
from cp2025.utility.algorithms import suppression

class SuppressionKAnonymityTimeOptimal(Depersonalizator):
    def __init__(self, k):
        super().__init__([0])
        self.k = k

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.k:
            return None, None, None

        hamming = dfs_hamming_distances(quasi_identifiers)
        groups = group_by_dist(hamming, self.k)

        n_suppressions, suppressed_df = suppression(groups, quasi_identifiers)

        return None, suppressed_df, n_suppressions

