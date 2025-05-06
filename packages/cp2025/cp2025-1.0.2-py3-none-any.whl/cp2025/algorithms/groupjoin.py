from cp2025.algorithms.Depersonalizator import Depersonalizator
import numpy as np
from cp2025.utility.algorithms import generalization, suppression, aggregation
from abc import abstractmethod, ABC
from cp2025.utility.statistics import mode
from cp2025.utility.metrics import real_sample_distance, get_elements_frequencies
from scipy.stats import entropy
import random
from cp2025.utility.utility import count_column_params_for_my_loss



class GroupJoinMethod(ABC):
    @abstractmethod
    def loss_real(self, array, col_ind):
        pass

    @abstractmethod
    def loss_ordered(self, array, col_ind):
        pass

    @abstractmethod
    def loss_unordered(self, array, col_ind):
        pass

    @abstractmethod
    def calc_columns_params(self, quasi_identifiers):
        pass

    @abstractmethod
    def depersonalize(self, groups, quasi_identifiers):
        pass


class GroupJoinSuppression(GroupJoinMethod):
    def __init__(self):
        super().__init__()
        self.columns_params = None
        self.quasi_identifiers_types = None

    def loss(self, array):
        n = len(set(array.tolist()))
        if n == 1:
            return 0
        else:
            return len(array)

    def loss_real(self, array, col_ind):
        return self.loss(array)

    def loss_ordered(self, array, col_ind):
        return self.loss(array)

    def loss_unordered(self, array, col_ind):
        return self.loss(array)

    def calc_columns_params(self, quasi_identifiers):
        self.columns_params = []

    def depersonalize(self, groups, quasi_identifiers):
        res = suppression(groups, quasi_identifiers)
        return res[1], res[0]

class GroupJoinGeneralization(GroupJoinMethod):
    def __init__(self, quasi_identifiers_types):
        super().__init__()
        self.quasi_identifiers_types = quasi_identifiers_types
        self.columns_params = None

    def loss_real(self, array, col_ind):
        mn = self.columns_params[col_ind][0]
        mx = self.columns_params[col_ind][1]
        arr_mn = np.min(array)
        arr_mx = np.max(array)
        if arr_mx == arr_mn:
            return 0
        loss = 0
        for el in array:
            loss += ((arr_mn - el) ** 2 + (arr_mx - el) ** 2) / (2 * (mx - mn) * (arr_mx - arr_mn))
        return loss

    def loss_ordered(self, array, col_ind):
        ranks = self.columns_params[col_ind][0]
        n = self.columns_params[col_ind][1]
        arr_min_rank = n
        arr_max_rank = 0
        for el in array:
            arr_min_rank = min(arr_min_rank, ranks[el])
            arr_max_rank = max(arr_max_rank, ranks[el])
        if arr_min_rank == arr_max_rank:
            return 0
        loss = 0
        for el in array:
            loss += ((arr_min_rank - ranks[el]) ** 2 + (arr_max_rank - ranks[el]) ** 2) / (2 * (n - 1) * (arr_max_rank - arr_min_rank))
        return loss

    def loss_unordered(self, array, col_ind):
        values_set = set(array.tolist())
        return len(array) - len(array) / len(values_set)

    def calc_columns_params(self, quasi_identifiers):
        self.columns_params = count_column_params_for_my_loss(quasi_identifiers, self.quasi_identifiers_types)

    def depersonalize(self, groups, quasi_identifiers):
        return generalization(groups, quasi_identifiers, self.quasi_identifiers_types)

class GroupJoinAggregation(GroupJoinMethod):
    def __init__(self, quasi_identifiers_types):
        super().__init__()
        self.quasi_identifiers_types = quasi_identifiers_types
        self.columns_params = None

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

    def calc_columns_params(self, quasi_identifiers):
        self.columns_params = count_column_params_for_my_loss(quasi_identifiers, self.quasi_identifiers_types)

    def depersonalize(self, groups, quasi_identifiers):
        return aggregation(groups, quasi_identifiers, self.quasi_identifiers_types)


class GroupJoinMetric(ABC):
    @abstractmethod
    def get_groups(self, quasi_identifiers, sensitives):
        pass

    @abstractmethod
    def loss(self, a, b):
        pass


class GroupJoinKAnonymity(GroupJoinMetric):
    def __init__(self, k, loss_function = lambda loss, size1, size2, k: loss, seed = None):
        super().__init__()
        self.k = k
        self.loss_function = loss_function
        self.group_join_method = None
        self.seed = seed

    def get_groups(self, quasi_identifiers, sensitives):
        if self.seed is not None:
            random.seed(self.seed)
        groups = [[i] for i in range(quasi_identifiers.shape[0])]
        groups_loss = [0 for i in range(quasi_identifiers.shape[0])]
        while not self.check_k_anonymity(groups):
            best_pair = (0, 1)
            best_loss = -1
            i = random.randint(0, len(groups)-1)
            while len(groups[i]) >= self.k:
                i = random.randint(0, len(groups)-1)
            for j in range(len(groups)):
                if i == j:
                    continue
                loss = self.loss(quasi_identifiers[groups[i], :], quasi_identifiers[groups[j], :])
                if best_loss == -1 or loss - groups_loss[i] - groups_loss[j] < best_loss - groups_loss[best_pair[0]] - \
                        groups_loss[best_pair[1]]:
                    best_loss = loss
                    best_pair = (min(i, j), max(i, j))
            new_group = groups[best_pair[0]] + groups[best_pair[1]]
            groups.pop(best_pair[1])
            groups.pop(best_pair[0])
            groups.append(new_group)
            groups_loss.pop(best_pair[1])
            groups_loss.pop(best_pair[0])
            groups_loss.append(best_loss)
        return groups

    def loss(self, a, b):
        loss = 0
        new_array = np.concatenate([a, b], axis=0)
        for i in range(a.shape[1]):
            if self.group_join_method.quasi_identifiers_types[i] == 'unordered':
                loss += self.group_join_method.loss_unordered(new_array[:, i], i)
            elif self.group_join_method.quasi_identifiers_types[i] == 'ordered':
                loss += self.group_join_method.loss_ordered(new_array[:, i], i)
            elif self.group_join_method.quasi_identifiers_types[i] == 'real':
                loss += self.group_join_method.loss_real(new_array[:, i], i)
        return self.loss_function(loss, a.shape[0], b.shape[0], self.k)

    def check_k_anonymity(self, groups):
        for group in groups:
            if len(group) < self.k:
                return False
        return True

class GroupJoinLDiversity(GroupJoinMetric):
    def __init__(self, k, l, loss_function = lambda loss, size1, size2, k, l, k_sens: loss / sum(k_sens), seed = None):
        super().__init__()
        self.k = k
        self.l = l
        self.loss_function = loss_function
        self.group_join_method = None
        self.seed = seed

    def get_groups(self, quasi_identifiers, sensitives):
        if self.seed is not None:
            random.seed(self.seed)
        groups = [[i] for i in range(quasi_identifiers.shape[0])]
        groups_loss = [0 for i in range(quasi_identifiers.shape[0])]
        while not self.check_l_diversity(groups, sensitives):
            best_pair = (0, 1)
            best_loss = -1
            i = random.randint(0, len(groups)-1)
            while self.check_l_diversity([list(range(len(groups[i])))], sensitives[groups[i],:]):
                i = random.randint(0, len(groups)-1)
            for j in range(len(groups)):
                if i == j:
                    continue
                loss = self.loss([quasi_identifiers[groups[i], :], sensitives[groups[i],:]], [quasi_identifiers[groups[j], :], sensitives[groups[j],:]])
                if best_loss == -1 or loss - groups_loss[i] - groups_loss[j] < best_loss - groups_loss[best_pair[0]] - \
                        groups_loss[best_pair[1]]:
                    best_loss = loss
                    best_pair = (min(i, j), max(i, j))
            new_group = groups[best_pair[0]] + groups[best_pair[1]]
            groups.pop(best_pair[1])
            groups.pop(best_pair[0])
            groups.append(new_group)
            groups_loss.pop(best_pair[1])
            groups_loss.pop(best_pair[0])
            groups_loss.append(best_loss)
        return groups

    def loss(self, a_data, b_data):
        a = a_data[0]
        b = b_data[0]
        a_sens = a_data[1]
        b_sens = b_data[1]
        new_k_sens = []
        for i in range(a_sens.shape[1]):
            new_k_sens.append(min(len(set(a_sens[:,i].tolist() + b_sens[:,i].tolist())), self.l))
        loss = 0
        new_array = np.concatenate([a, b], axis=0)
        for i in range(a.shape[1]):
            if self.group_join_method.quasi_identifiers_types[i] == 'unordered':
                loss += self.group_join_method.loss_unordered(new_array[:, i], i)
            elif self.group_join_method.quasi_identifiers_types[i] == 'ordered':
                loss += self.group_join_method.loss_ordered(new_array[:, i], i)
            elif self.group_join_method.quasi_identifiers_types[i] == 'real':
                loss += self.group_join_method.loss_real(new_array[:, i], i)
        return self.loss_function(loss, a.shape[0], b.shape[0], self.k, self.l, new_k_sens)

    def check_l_diversity(self, groups, sensitives):
        for group in groups:
            if len(group) < self.k:
                return False
            for i in range(sensitives.shape[1]):
                if len(set(sensitives[group, i].tolist())) < self.l:
                    return False
        return True

class GroupJoinTCloseness(GroupJoinMetric):
    def __init__(self, k, t, sensitives_types, loss_function = lambda loss, size1, size2, k, t, t_sens: loss * sum(t_sens), always_use_entropy = False, seed = None):
        super().__init__()
        self.k = k
        self.t = t
        self.loss_function = loss_function
        self.group_join_method = None
        self.sensitives_types = sensitives_types
        self.always_use_entropy = always_use_entropy
        self.sensitives = None
        self.elements_set = []
        self.sensitives_frequencies = []
        self.seed = seed

    def prepare_statistics(self, sensitives):
        self.sensitives = sensitives
        for i in range(sensitives.shape[1]):
            self.elements_set.append(set(sensitives[:, i].tolist()))
            self.sensitives_frequencies.append(get_elements_frequencies(sensitives[:, i].tolist(), self.elements_set[i]))

    def get_groups(self, quasi_identifiers, sensitives):
        if self.seed is not None:
            random.seed(self.seed)
        groups = [[i] for i in range(quasi_identifiers.shape[0])]
        groups_loss = [0 for i in range(quasi_identifiers.shape[0])]
        self.prepare_statistics(sensitives)
        while not self.check_t_closeness(groups, sensitives):
            best_pair = (0, 1)
            best_loss = -1
            i = random.randint(0, len(groups)-1)
            while self.check_t_closeness([list(range(len(groups[i])))], sensitives[groups[i],:]):
                i = random.randint(0, len(groups)-1)
            for j in range(len(groups)):
                if i == j:
                    continue
                loss = self.loss([quasi_identifiers[groups[i], :], sensitives[groups[i],:]], [quasi_identifiers[groups[j], :], sensitives[groups[j],:]])
                if best_loss == -1 or loss - groups_loss[i] - groups_loss[j] < best_loss - groups_loss[best_pair[0]] - \
                        groups_loss[best_pair[1]]:
                    best_loss = loss
                    best_pair = (min(i, j), max(i, j))
            new_group = groups[best_pair[0]] + groups[best_pair[1]]
            groups.pop(best_pair[1])
            groups.pop(best_pair[0])
            groups.append(new_group)
            groups_loss.pop(best_pair[1])
            groups_loss.pop(best_pair[0])
            groups_loss.append(best_loss)
        return groups

    def loss(self, a_data, b_data):
        a = a_data[0]
        b = b_data[0]
        a_sens = a_data[1]
        b_sens = b_data[1]
        all_sens = np.concatenate([a_sens, b_sens], axis=0)
        t_sens = []
        for i in range(all_sens.shape[1]):
            if self.always_use_entropy or self.sensitives_types[i] != 'real':
                t_sens.append(self.categorical_sample_distance(all_sens[:,i], i))
            else:
                t_sens.append(real_sample_distance(all_sens[:,i], self.sensitives[:,i]))
        loss = 0
        new_array = np.concatenate([a, b], axis=0)
        for i in range(a.shape[1]):
            if self.group_join_method.quasi_identifiers_types[i] == 'unordered':
                loss += self.group_join_method.loss_unordered(new_array[:, i], i)
            elif self.group_join_method.quasi_identifiers_types[i] == 'ordered':
                loss += self.group_join_method.loss_ordered(new_array[:, i], i)
            elif self.group_join_method.quasi_identifiers_types[i] == 'real':
                loss += self.group_join_method.loss_real(new_array[:, i], i)
        return self.loss_function(loss, a.shape[0], b.shape[0], self.k, self.t, t_sens)

    def categorical_sample_distance(self, p, ind):
        if not isinstance(p, list):
            p = p.tolist()
        p_frequencies = get_elements_frequencies(p, self.elements_set[ind])
        avg_frequencies = (p_frequencies + self.sensitives_frequencies[ind]) / 2
        return (entropy(p_frequencies, avg_frequencies) + entropy(self.sensitives_frequencies[ind], avg_frequencies)) / 2

    def check_t_closeness(self, groups, sensitives):
        for group in groups:
            if len(group) < self.k:
                return False
            for i in range(sensitives.shape[1]):
                if self.always_use_entropy or self.sensitives_types[i] != 'real':
                    if self.categorical_sample_distance(sensitives[group,i], i) > self.t:
                        return False
                else:
                    if real_sample_distance(sensitives[:, i], sensitives[group, i]) > self.t:
                        return False
        return True

class GroupJoinDepersonalizator(Depersonalizator):
    def __init__(self, group_join_method, group_join_metric):
        super().__init__([0])
        self.group_join_method = group_join_method
        self.group_join_metric = group_join_metric
        self.group_join_metric.group_join_method = group_join_method

    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        if len(quasi_identifiers) == 0:
            return None, quasi_identifiers, 0

        if len(quasi_identifiers) < self.group_join_metric.k:
            return None, None, None

        if self.group_join_method.quasi_identifiers_types is None:
            self.group_join_method.quasi_identifiers_types = ['unordered'] * len(quasi_identifiers[0])

        self.group_join_method.calc_columns_params(quasi_identifiers)
        groups = self.group_join_metric.get_groups(quasi_identifiers, sensitives)
        self.groups = groups
        return None, *self.group_join_method.depersonalize(groups, quasi_identifiers)

if __name__ == '__main__':
    #gjmth = GroupJoinGeneralization(['real']*4)
    gjmth = GroupJoinAggregation(['real']*4)
    #gjmth = GroupJoinSuppression()
    #gjmtc = GroupJoinKAnonymity(2)
    #gjmtc = GroupJoinLDiversity(2, 2)
    gjmtc = GroupJoinTCloseness(2, 0.075, ['unordered'])
    dep = GroupJoinDepersonalizator(gjmth, gjmtc)
    df = [
        [1, 1, 1, 1, 'a'],
        [1, 1, 1, 2, 'b'],
        [1, 1, 1, 3, 'c'],
        [1, 4, 4, 4, 'a'],
        [1, 4, 4, 5, 'b'],
    ]
    k_anonymus_df, k_generalizations = dep.depersonalize(df, sensitives_ids=[4])
    print(k_anonymus_df, k_generalizations)

