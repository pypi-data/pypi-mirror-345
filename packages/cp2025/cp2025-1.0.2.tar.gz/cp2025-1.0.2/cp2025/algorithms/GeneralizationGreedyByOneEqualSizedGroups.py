from cp2025.algorithms.Depersonalizator import Depersonalizator
import numpy as np
from cp2025.utility.GeneralizationRange import GeneralizationRange
from cp2025.utility.metrics import is_k_anonimus


class GeneralizationGreedyByOneEqualSizedGroups(Depersonalizator):
    def __init__(self, k, quasi_identifiers_types = None):
        super().__init__([0])
        self.k = k
        self.quasi_identifiers_types = quasi_identifiers_types

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.k:
            return None, None, None

        if self.quasi_identifiers_types is None:
            self.quasi_identifiers_types = ['unordered'] * len(quasi_identifiers[0])

        group_size = max(self.k-1, 1)
        aggregated_quasi_identifiers = np.copy(quasi_identifiers)

        while not is_k_anonimus(aggregated_quasi_identifiers, self.k):
            group_size+=1
            aggregated_quasi_identifiers = self.__generalize__(np.copy(quasi_identifiers), group_size)

        return None, aggregated_quasi_identifiers, group_size

    def __generalize__(self, quasi_identifiers, group_size):
        for i in range(len(quasi_identifiers[0])):
            quasi_identifiers[:, i] = self.__generalize_column__(quasi_identifiers[:, i], group_size, self.quasi_identifiers_types[i])

        return quasi_identifiers

    def __generalize_column__(self, column, group_size, column_type):
        group_values = []
        group_mins = []
        group_maxs = []
        if column_type == 'unordered':
            values = np.array(list(set(column.tolist())))
            i=0
            group_values = []
            pred_i = 0
            while i < len(values):
                k_lines = 0
                while i < len(values) and k_lines < group_size:
                    k_lines += (column == values[i]).sum()
                    i+=1
                if k_lines < group_size:
                    group_values[-1] = group_values[-1] + values[pred_i:].tolist()
                else:
                    group_values.append(values[pred_i:i].tolist())
                pred_i = i
            for group in group_values:
                generalized_value = GeneralizationRange(None, None, 'unordered', np.array(group)) if len(group) != 1 else group[0]
                for value in group:
                    column[column == value] = generalized_value
            return column
        elif column_type == 'ordered' or column_type == 'real':
            sorted_column = np.sort(column)
            i = 0
            last_grouped_id = -1
            while i < len(sorted_column) and len(sorted_column) - i >= group_size:
                while i < len(sorted_column) and not (i - last_grouped_id >= group_size and (i + 1 >= len(sorted_column) or sorted_column[i] != sorted_column[i+1])):
                    i += 1
                if i == len(sorted_column):
                    i-=1
                group_mins.append(sorted_column[last_grouped_id+1])
                group_maxs.append(sorted_column[i])
                group_values.append(np.unique(sorted_column[last_grouped_id+1:i+1]))
                last_grouped_id = i
                i += 1
            if i != len(sorted_column):
                group_maxs[-1]=sorted_column[-1]
                group_values[-1]=np.unique(np.concatenate((group_values[-1], sorted_column[i:])))
            for i in range(len(group_mins)):
                generalized_value = GeneralizationRange(group_mins[i], group_maxs[i], column_type) if group_mins[i] != group_maxs[i] else group_mins[i]
                for value in group_values[i]:
                    column[column == value] = generalized_value
            return column
        return column