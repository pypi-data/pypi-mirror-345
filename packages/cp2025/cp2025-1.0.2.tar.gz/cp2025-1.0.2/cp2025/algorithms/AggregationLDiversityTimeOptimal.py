from cp2025.algorithms.Depersonalizator import Depersonalizator
from cp2025.utility.diatances import dfs_rank_general_dist
from cp2025.utility.groupping import group_by_dist_with_l_diverse
from cp2025.utility.algorithms import aggregation

class AggregationLDiversityTimeOptimal(Depersonalizator):
    def __init__(self, k, l, quasi_identifiers_types = None):
        super().__init__([0])
        self.k = k
        self.l = l
        self.quasi_identifiers_types = quasi_identifiers_types

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.k:
            return None, None, None

        if self.quasi_identifiers_types is None:
            self.quasi_identifiers_types = ['unordered'] * len(quasi_identifiers[0])

        my_dist = dfs_rank_general_dist(quasi_identifiers, self.quasi_identifiers_types)
        groups = group_by_dist_with_l_diverse(my_dist, sensitives, self.k, self.l)
        if groups is None:
            return None, None, None

        generalized_df, n_generalizations = aggregation(groups, quasi_identifiers, self.quasi_identifiers_types)

        return None, generalized_df, n_generalizations
