import numpy as np

def fill_left_columns_ids(size, other_list_1, other_list_2):
    has_left = [True] * size
    for i in other_list_1:
        has_left[i] = False
    for i in other_list_2:
        has_left[i] = False
    left = []
    for i in range(size):
        if has_left[i]:
            left.append(i)
    return left

def count_column_params_for_my_loss(quasi_identifiers, quasi_identifiers_types):
    columns_params = []
    for i in range(len(quasi_identifiers[1])):
        if quasi_identifiers_types[i] == 'unordered':
            columns_params.append([])
        elif quasi_identifiers_types[i] == 'ordered':
            ranks = dict()
            sorted_col = quasi_identifiers[:, i]
            np.sort(sorted_col)
            for j in range(len(sorted_col)):
                if sorted_col[j] not in ranks:
                    ranks[sorted_col[j]] = j
            columns_params.append([ranks, len(sorted_col)])
        elif quasi_identifiers_types[i] == 'real':
            mn = np.min(quasi_identifiers[:, i])
            mx = np.max(quasi_identifiers[:, i])
            columns_params.append([mn, mx])
    return columns_params