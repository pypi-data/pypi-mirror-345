import numpy as np
from cp2025.utility.GeneralizationRange import GeneralizationRange
from statistics import mode

def suppression(groups, quasi_identifiers):
    n_suppressions = 0
    suppressed_df = np.zeros(quasi_identifiers.shape, dtype=object)
    for group in groups:
        mask = quasi_identifiers[group[0]] == quasi_identifiers[group[0]]
        for i in range(1, len(group)):
            mask = mask & (quasi_identifiers[group[0]] == quasi_identifiers[group[i]])
        mask = ~mask
        for i in group:
            row = quasi_identifiers[i].copy()
            row[mask] = np.nan
            n_suppressions += mask.sum()
            suppressed_df[i] = row
    return n_suppressions, suppressed_df


def generalization(groups, quasi_identifiers, quasi_identifiers_types):
    n_generalizations = 0
    generalized_df = np.zeros(quasi_identifiers.shape, dtype=object)
    for group in groups:
        mask = quasi_identifiers[group[0]] == quasi_identifiers[group[0]]
        mn = quasi_identifiers[group[0]].copy()
        mx = quasi_identifiers[group[0]].copy()
        for i in range(len(group)):
            mask = mask & (quasi_identifiers[group[0]] == quasi_identifiers[group[i]])
            for j in range(mn.shape[0]):
                if quasi_identifiers_types[j] != 'unordered':
                    mn[j] = min(mn[j], quasi_identifiers[group[i]][j])
                    mx[j] = max(mn[j], quasi_identifiers[group[i]][j])
        rng = np.array(list(map(lambda x: GeneralizationRange(x[0], x[1], x[2], x[3]),
                                zip(mn, mx, quasi_identifiers_types, np.transpose(quasi_identifiers[group])))))
        mask = ~mask
        for i in group:
            row = quasi_identifiers[i].copy()
            row[mask] = rng[mask]
            n_generalizations += mask.sum()
            generalized_df[i] = row

    return generalized_df, n_generalizations

def aggregation(groups, quasi_identifiers, quasi_identifiers_types):
    aggregated_df = np.zeros(quasi_identifiers.shape, dtype=object)

    for group in groups:
        mask = quasi_identifiers[group[0]] == quasi_identifiers[group[0]]
        aggregated_row = quasi_identifiers[group[0]].copy()
        for i in range(len(group)):
            mask = mask & (quasi_identifiers[group[0]] == quasi_identifiers[group[i]])
        for i in range(quasi_identifiers.shape[1]):
            if not mask[i]:
                if quasi_identifiers_types[i] == 'real':
                    aggregated_row[i] = np.mean(quasi_identifiers[group, i])
                elif quasi_identifiers_types[i] == 'ordered':
                    aggregated_row[i] = np.median(quasi_identifiers[group, i])
                elif quasi_identifiers_types[i] == 'unordered':
                    aggregated_row[i] = mode(quasi_identifiers[group, i])
                else:
                    aggregated_row[i] = np.nan
        for i in group:
            aggregated_df[i] = aggregated_row

    n_replaced = (aggregated_df != quasi_identifiers).sum()

    return aggregated_df, n_replaced

