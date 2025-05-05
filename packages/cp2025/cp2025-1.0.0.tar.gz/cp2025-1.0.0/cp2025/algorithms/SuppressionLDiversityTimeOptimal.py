from cp2025.algorithms.Depersonalizator import Depersonalizator
from cp2025.utility.diatances import dfs_hamming_distances
from cp2025.utility.groupping import group_by_dist_with_l_diverse
from cp2025.utility.algorithms import suppression

class SuppressionLDiversityTimeOptimal(Depersonalizator):
    def __init__(self, k, l):
        super().__init__([0])
        self.k = k
        self.l = l

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.k:
            return None, None, None

        hamming = dfs_hamming_distances(quasi_identifiers)
        groups = group_by_dist_with_l_diverse(hamming, sensitives, self.k, self.l)
        if groups is None:
            return None, None, None

        n_suppressions, suppressed_df = suppression(groups, quasi_identifiers)

        return None, suppressed_df, n_suppressions

