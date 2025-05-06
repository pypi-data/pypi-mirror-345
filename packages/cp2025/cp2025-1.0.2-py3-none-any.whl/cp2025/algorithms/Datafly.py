from cp2025.algorithms.Depersonalizator import Depersonalizator
import numpy as np
from cp2025.utility.GeneralizationRange import join_unordered, join_ordered


class Datafly(Depersonalizator):
    def __init__(self, k, quasi_identifiers_types = None, k_suppressed_lines = None):
        super().__init__([0])
        self.k = k
        self.quasi_identifiers_types = quasi_identifiers_types
        if k_suppressed_lines is not None:
            self.k_suppressed_lines = k_suppressed_lines
        else:
            self.k_suppressed_lines = k-1

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.k:
            return None, None, None

        if self.quasi_identifiers_types is None:
            self.quasi_identifiers_types = ['unordered'] * len(quasi_identifiers[0])

        quasi_identifiers_initial = np.copy(quasi_identifiers)
        while not self.__has_less_k_suppressed_not_grouped__(quasi_identifiers):
            column_with_max_distinct = 0
            max_k_distinct = 0
            for i in range(len(quasi_identifiers[0])):
                k_distinct = len(set(quasi_identifiers[:, i].tolist()))
                if k_distinct > max_k_distinct:
                    max_k_distinct = k_distinct
                    column_with_max_distinct = i
            quasi_identifiers[:,column_with_max_distinct] = (
                self.__generalize_column__(quasi_identifiers[:,column_with_max_distinct],
                                           self.quasi_identifiers_types[column_with_max_distinct]))

        quasi_identifiers = self.__supress_not_k_anonymus__(quasi_identifiers)
        k_changes = (quasi_identifiers_initial != quasi_identifiers).sum()

        return None, quasi_identifiers, k_changes

    def __get_k_lines_dict__(self, quasi_identifiers):
        k_lines = dict()
        for i in range(len(quasi_identifiers)):
            if tuple(quasi_identifiers[i]) not in k_lines:
                k_lines[tuple(quasi_identifiers[i])] = [i]
            else:
                k_lines[tuple(quasi_identifiers[i])].append(i)
        return k_lines

    def __has_less_k_suppressed_not_grouped__(self, quasi_identifiers):
        k_lines = self.__get_k_lines_dict__(quasi_identifiers)
        k_not_grouped = 0
        for line in k_lines.keys():
            if len(k_lines[line]) < self.k:
                k_not_grouped += len(k_lines[line])
        return k_not_grouped <= self.k_suppressed_lines

    def __generalize_column__(self, column, column_type):
        if column_type == 'unordered':
            values = list(set(column.tolist()))
            values_count = dict()
            for value in column.tolist():
                if value not in values_count:
                    values_count[value] = 1
                else:
                    values_count[value] += 1
            count = [0] * len(values)
            for i in range(len(values)):
                count[i] = values_count[values[i]]
            values = np.array(values)
            count = np.array(count)
            count_sorted = np.sort(count)
            min_count_value = values[np.where(count == count_sorted[0])[0][0]]
            second_min_count_value = values[np.where(count == count_sorted[1])[0][0]] if count_sorted[0] != count_sorted[1] \
                else values[np.where(count == count_sorted[1])[0][1]]
            generalized_value = join_unordered(min_count_value, second_min_count_value)
            column[column == min_count_value] = generalized_value
            column[column == second_min_count_value] = generalized_value
            return column
        elif column_type == 'real' or column_type == 'ordered':
            values, count = np.unique(column, return_counts=True)
            values_count = dict(zip(values, count))
            count_sorted = np.sort(count)
            min_count_value = values[np.where(count == count_sorted[0])[0][0]]

            column_sorted = np.sort(np.copy(column))
            less_min_count_value_id = np.where(column_sorted == min_count_value)[0][0]
            more_min_count_value_id = np.where(column_sorted == min_count_value)[0][0]
            while less_min_count_value_id >= 0 and column_sorted[less_min_count_value_id] == min_count_value:
                less_min_count_value_id -= 1
            while more_min_count_value_id < len(column) and column_sorted[more_min_count_value_id] == min_count_value:
                more_min_count_value_id += 1
            if less_min_count_value_id == -1:
                second_generalization_value = column_sorted[more_min_count_value_id]
            elif more_min_count_value_id == len(column):
                second_generalization_value = column_sorted[less_min_count_value_id]
            elif values_count[column_sorted[less_min_count_value_id]] > values_count[column_sorted[more_min_count_value_id]]:
                second_generalization_value = column_sorted[more_min_count_value_id]
            else:
                second_generalization_value = column_sorted[less_min_count_value_id]
            generalized_value = join_ordered(min_count_value, second_generalization_value, column_type)
            column[column == min_count_value] = generalized_value
            column[column == second_generalization_value] = generalized_value
            return column
        return column

    def __supress_not_k_anonymus__(self, quasi_identifiers):
        k_lines = self.__get_k_lines_dict__(quasi_identifiers)
        for line in k_lines.keys():
            if len(k_lines[line]) < self.k:
                for i in k_lines[line]:
                    quasi_identifiers[i] = np.array([np.nan] * len(quasi_identifiers[0]))
        return quasi_identifiers