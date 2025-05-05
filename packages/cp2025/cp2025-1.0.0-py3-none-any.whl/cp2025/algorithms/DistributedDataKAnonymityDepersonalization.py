import random
import numpy as np
from cp2025.utility.algorithms import mode, suppression, aggregation
from groupjoin import GroupJoinKAnonymity, GroupJoinAggregation, GroupJoinDepersonalizator
from cp2025.utility.utility import count_column_params_for_my_loss
from ecpy.curves import Curve, Point

class DistributedDataOwnerKAnonymityDepersonalizator:
    def __init__(self, quasi_identifiers, sensitives, k, encryption_key, quasi_identifiers_types = None, seed = None):
        self.__quasi_identifiers = quasi_identifiers
        self.__sensitives = sensitives
        self.k = k
        if quasi_identifiers_types is None:
            quasi_identifiers_types = ['unordered'] * quasi_identifiers.shape[1]
        self.quasi_identifiers_types = quasi_identifiers_types
        self.__depersonalization_groups = [[i] for i in range(quasi_identifiers.shape[0])]
        self.__groups_loss = [0 for i in range(quasi_identifiers.shape[0])]
        self.dps = GroupJoinDepersonalizator(GroupJoinAggregation(self.quasi_identifiers_types), GroupJoinKAnonymity(self.k))
        self.__encryption_key = encryption_key
        self.cv = Curve.get_curve('secp256k1')
        self.other_data_owner = None
        self.joined_data = None
        self.seed = seed
        self.columns_params = None
        self.elliptic_point = None

    def set_other_data_owner(self, other_data_owner):
        self.other_data_owner = other_data_owner

    def depersonalize_local(self):
        self.dps.depersonalize(self.__quasi_identifiers)
        self.__depersonalization_groups = self.dps.groups

    def depersonalize_step(self):
        best_pair = (0, 1)
        best_loss = -1
        i = 0
        for j in range(len(self.__depersonalization_groups)):
            if len(self.__depersonalization_groups[i]) > len(self.__depersonalization_groups[j]):
                i = j
        for j in range(len(self.__depersonalization_groups)):
            if i == j:
                continue
            loss = self.loss(self.__quasi_identifiers[self.__depersonalization_groups[i], :], self.__quasi_identifiers[self.__depersonalization_groups[j], :])
            if best_loss == -1 or loss - self.__groups_loss[i] - self.__groups_loss[j] < best_loss - self.__groups_loss[best_pair[0]] - self.__groups_loss[best_pair[1]]:
                best_loss = loss
                best_pair = (min(i, j), max(i, j))
        new_group = self.__depersonalization_groups[best_pair[0]] + self.__depersonalization_groups[best_pair[1]]
        self.__depersonalization_groups.pop(best_pair[1])
        self.__depersonalization_groups.pop(best_pair[0])
        self.__depersonalization_groups.append(new_group)
        self.__groups_loss.pop(best_pair[1])
        self.__groups_loss.pop(best_pair[0])
        self.__groups_loss.append(best_loss)

    def loss(self, a, b):
        loss = 0
        new_array = np.concatenate([a, b], axis=0)
        for i in range(a.shape[1]):
            if self.quasi_identifiers_types[i] == 'unordered':
                loss += self.loss_unordered(new_array[:, i], i)
            elif self.quasi_identifiers_types[i] == 'ordered':
                loss += self.loss_ordered(new_array[:, i], i)
            elif self.quasi_identifiers_types[i] == 'real':
                loss += self.loss_real(new_array[:, i], i)
        return loss

    def loss_real(self, array, col_ind):
        mn = self.columns_params[col_ind][0]
        mx = self.columns_params[col_ind][1]
        avg = np.mean(array)
        if mn == mx:
            return 0
        return np.sum(np.abs(array - avg)) / (mx - mn)

    def loss_ordered(self, array, col_ind):
        ranks = self.columns_params[col_ind][0]
        n = self.columns_params[col_ind][1]
        md = np.median(array)
        loss = 0
        for el in array:
            loss += abs(ranks[el] - md) / (n - 1)
        return loss

    def loss_unordered(self, array, col_ind):
        md = mode(array)
        return np.sum(array != md)

    def get_encoded_depersonalization_groups(self):
        return self.encode_groups(self.__depersonalization_groups)

    def encode_groups(self, groups):
        encoded_groups = []
        for group in groups:
            encoded_group = []
            for ind in group:
                if isinstance(ind, Point):
                    encoded_group.append(self.__encryption_key * ind)
                else:
                    encoded_group.append(self.__encryption_key * ind * self.elliptic_point)
            encoded_groups.append(encoded_group)
        return encoded_groups

    def get_depersonalized_data(self):
        depersonalized_qi = aggregation(self.__depersonalization_groups, self.__quasi_identifiers, self.quasi_identifiers_types)[0]
        if len(self.__sensitives) > 0:
            return np.concatenate((depersonalized_qi, self.__sensitives), axis=1)
        else:
            return depersonalized_qi

    def get_encoded_groups(self):
        groups_1 = self.other_data_owner.encode_groups(self.get_encoded_depersonalization_groups())
        groups_2 = self.encode_groups(self.other_data_owner.get_encoded_depersonalization_groups())
        return groups_1, groups_2

    def exchange_depersonalized_data(self, other_quasi_identifiers):
        groups_1, groups_2 = self.get_encoded_groups()
        if self.are_equal(groups_1, groups_2):
            self.joined_data = np.concatenate((other_quasi_identifiers, self.get_depersonalized_data()), axis=1)
            return self.joined_data
        return None

    def count_columns_params(self):
        self.columns_params = count_column_params_for_my_loss(self.__quasi_identifiers, self.quasi_identifiers_types)

    def exchange_data(self):
        if self.seed is not None:
            random.seed(self.seed)
        self.depersonalize_local()
        self.other_data_owner.depersonalize_local()

        self.elliptic_point = self.cv.generator
        self.other_data_owner.elliptic_point = self.elliptic_point

        self.count_columns_params()
        self.other_data_owner.count_columns_params()

        groups_1, groups_2 = self.get_encoded_groups()
        while not self.are_equal(groups_1, groups_2):
            self.depersonalize_step()
            self.other_data_owner.depersonalize_step()
            groups_1, groups_2 = self.get_encoded_groups()

        self.joined_data = self.other_data_owner.exchange_depersonalized_data(self.get_depersonalized_data())

    def get_ind_group_dict(self, groups):
        ind_group = dict()
        for i in range(len(groups)):
            for ind in groups[i]:
                ind_group[str(ind)] = i
        return ind_group

    def are_equal(self, groups1, groups2):
        ind_group1 = self.get_ind_group_dict(groups1)
        ind_group2 = self.get_ind_group_dict(groups2)
        inds_checked = dict()
        for ind in ind_group1:
            inds_checked[str(ind)] = False
        for group in groups1:
            group_set = set([str(gr_ind) for gr_ind in group])
            for ind in group:
                if not inds_checked[str(ind)]:
                    group2_of_ind = ind_group2[str(ind)]
                    groups_intersection = group_set.intersection(set([str(gr_ind) for gr_ind in groups2[group2_of_ind]]))
                    if len(groups_intersection) < self.k:
                        return False
                    for ind_checked in groups_intersection:
                        inds_checked[ind_checked] = True
        return True

if __name__ == '__main__':
    qi1= np.array([
        [1, 1, 1],
        [1, 1, 2],
        [3, 3, 3],
        [3, 3, 4],
        [4, 4, 5],
        [4, 4, 4],
    ], dtype=object)
    qi2 = np.array([
        [1, 1, 1],
        [1, 1, 2],
        [3, 3, 3],
        [4, 4, 5],
        [3, 3, 4],
        [4, 4, 4],
    ], dtype=object)
    s1= np.array([])#np.array([[1],[2],[3],[4],[5],[6]], dtype=object)
    s2= np.array([])#np.array([[1],[2],[3],[5],[6],[7]], dtype=object)
    dep1 = DistributedDataOwnerKAnonymityDepersonalizator(qi1,s1,2, 7,seed=7,quasi_identifiers_types=['real']*qi1.shape[1])
    dep2 = DistributedDataOwnerKAnonymityDepersonalizator(qi2,s2,2, 8, seed=7,quasi_identifiers_types=['real']*qi2.shape[1])
    dep1.set_other_data_owner(dep2)
    dep2.set_other_data_owner(dep1)
    dep1.exchange_data()
    print(dep1.joined_data)
