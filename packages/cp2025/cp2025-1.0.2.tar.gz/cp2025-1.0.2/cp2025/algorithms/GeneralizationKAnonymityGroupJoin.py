from cp2025.algorithms.Depersonalizator import Depersonalizator
import numpy as np
from cp2025.utility.algorithms import generalization


class GeneralizationKAnonymityGroupJoin(Depersonalizator):
    def __init__(self, k, quasi_identifiers_types = None, loss_function = lambda loss, size1, size2, k: loss):
        super().__init__([0])
        self.k = k
        self.quasi_identifiers_types = quasi_identifiers_types
        self.loss_function = loss_function

    def __loss_real(self, array, mn, mx):
        arr_mn = np.min(array)
        arr_mx = np.max(array)
        loss = 0
        for el in array:
            loss += ((arr_mn - el)**2 + (arr_mx - el)**2) / (mx - mn)**2
        return loss

    def __loss_ordered(self, array, ranks, n):
        arr_min_rank = n
        arr_max_rank = 0
        for el in array:
            arr_min_rank = min(arr_min_rank, ranks[el])
            arr_max_rank = max(arr_max_rank, ranks[el])
        loss = 0
        for el in array:
            loss += ((arr_min_rank - ranks[el])**2 + (arr_max_rank - ranks[el])**2) / (n - 1)**2
        return loss

    def __loss_unordered(self, array):
        values_set = set(array.tolist())
        return len(array) - len(array) / len(values_set)

    def __loss(self, a, b, columns_params, columns_types):
        loss = 0
        new_array = np.concatenate([a, b], axis=0)
        for i in range(a.shape[1]):
            if columns_types[i] == 'unordered':
                loss += self.__loss_unordered(new_array[:, i])
            elif columns_types[i] == 'ordered':
                loss += self.__loss_ordered(new_array[:, i], columns_params[i][0], columns_params[i][1])
            elif columns_types[i] == 'real':
                loss += self.__loss_real(new_array[:, i], columns_params[i][0], columns_params[i][1])
        return self.loss_function(loss, a.shape[0], b.shape[0], self.k)

    def __check_groups_k_anonymus(self, groups, k):
        for group in groups:
            if len(group) < k:
                return False
        return True

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.k:
            return None, None, None

        if self.quasi_identifiers_types is None:
            self.quasi_identifiers_types = ['unordered'] * len(quasi_identifiers[0])

        columns_params = []
        for i in range(len(quasi_identifiers[1])):
            if self.quasi_identifiers_types[i] == 'unordered':
                columns_params.append([])
            elif self.quasi_identifiers_types[i] == 'ordered':
                ranks = dict()
                sorted_col = quasi_identifiers[:,i]
                np.sort(sorted_col)
                for j in range(len(sorted_col)):
                    if sorted_col[j] not in ranks:
                        ranks[sorted_col[j]] = j
                columns_params.append([ranks, len(sorted_col)])
            elif self.quasi_identifiers_types[i] == 'real':
                mn = np.min(quasi_identifiers[:,i])
                mx = np.max(quasi_identifiers[:,i])
                columns_params.append([mn,mx])

        groups = [[i] for i in range(quasi_identifiers.shape[0])]
        groups_loss = [0 for i in range(quasi_identifiers.shape[0])]
        while not self.__check_groups_k_anonymus(groups, self.k):
            best_pair = (0, 1)
            best_loss = -1
            i = 0
            while len(groups[i]) >= self.k:
                i+=1
            for j in range(len(groups)):
                if i==j:
                    continue
                loss = self.__loss(quasi_identifiers[groups[i],:], quasi_identifiers[groups[j],:], columns_params, self.quasi_identifiers_types)
                if best_loss == -1 or loss - groups_loss[i] - groups_loss[j] < best_loss - groups_loss[best_pair[0]] - groups_loss[best_pair[1]]:
                    best_loss = loss
                    best_pair = (min(i, j), max(i, j))
            new_group = groups[best_pair[0]] + groups[best_pair[1]]
            groups.pop(best_pair[1])
            groups.pop(best_pair[0])
            groups.append(new_group)
            groups_loss.pop(best_pair[1])
            groups_loss.pop(best_pair[0])
            groups_loss.append(best_loss)

        generalized_df, n_generalizations = generalization(groups, quasi_identifiers, self.quasi_identifiers_types)

        return None, generalized_df, n_generalizations

