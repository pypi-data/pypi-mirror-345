import numpy as np
from scipy.stats import entropy
from scipy.stats import wasserstein_distance
from cp2025.utility.GeneralizationRange import GeneralizationRange
from cp2025.utility.prepare_data import is_nan

def is_k_anonimus_v0(df, k):
    for current_row in df:
        kol = 0
        for row in df:
            kol += (row == current_row).all()
        if kol < k:
            return False
    return True

def is_k_anonimus(df, k):
    counts = dict()
    for row in df:
        if tuple(row.tolist()) in counts:
            counts[tuple(row.tolist())] += 1
        else:
            counts[tuple(row.tolist())] = 1
    for _, count in counts.items():
        if count < k:
            return False
    return True

def is_l_diverse(quasi_identifiers, sensitives, k, l):
    counts = dict()
    sensitive_values = dict()
    for identifiers, sensitive in zip(quasi_identifiers, sensitives):
        if tuple(identifiers.tolist()) in counts:
            counts[tuple(identifiers.tolist())] += 1
            sensitive_values[tuple(identifiers.tolist())].add(tuple(sensitive.tolist()))
        else:
            counts[tuple(identifiers.tolist())] = 1
            sensitive_values[tuple(identifiers.tolist())] = set()
            sensitive_values[tuple(identifiers.tolist())].add(tuple(sensitive.tolist()))
    for key in counts.keys():
        if counts[key] < k:
            return False
        batch_sensitives = np.stack(list(sensitive_values[key]), axis=0)
        for i in range(batch_sensitives.shape[1]):
            if len(set(batch_sensitives[:,i].tolist())) < l:
                return False
    return True

def get_elements_frequencies(array, elements_set):
    count = dict()
    for el in elements_set:
        count[el] = 0
    for el in array:
        count[el] += 1
    return np.array([count[el] for el in elements_set]) / len(array)

def real_sample_distance(p, q):
    mn = min(p.min(), q.min())
    mx = max(p.max(), q.max())
    e = 1e-10
    return wasserstein_distance(p, q) / (mx - mn + e)

def categorical_sample_distance(p, q):
    if not isinstance(p, list):
        p = p.tolist()
    if not isinstance(q, list):
        q = q.tolist()
    elements_set = set(p + q)
    p_frequencies = get_elements_frequencies(p, elements_set)
    q_frequencies = get_elements_frequencies(q, elements_set)
    avg_frequencies = (p_frequencies + q_frequencies) / 2
    return (entropy(p_frequencies, avg_frequencies) + entropy(q_frequencies, avg_frequencies)) / 2

def is_t_close(quasi_identifiers, sensitives, sensitives_types, k, t, always_use_entropy = False):
    counts = dict()
    sensitive_values = dict()
    for identifiers, sensitive in zip(quasi_identifiers, sensitives):
        if tuple(identifiers.tolist()) in counts:
            counts[tuple(identifiers.tolist())] += 1
            sensitive_values[tuple(identifiers.tolist())].append(sensitive)
        else:
            counts[tuple(identifiers.tolist())] = 1
            sensitive_values[tuple(identifiers.tolist())] = list()
            sensitive_values[tuple(identifiers.tolist())].append(sensitive)
    for key in counts.keys():
        if counts[key] < k:
            return False
        batch_sensitives = np.stack(list(sensitive_values[key]), axis=0)
        for i in range(batch_sensitives.shape[1]):
            if sensitives_types[i] == 'real' and not always_use_entropy:
                if real_sample_distance(sensitives[:, i], batch_sensitives[:, i]) > t:
                    return False
            else:
                if categorical_sample_distance(sensitives[:, i], batch_sensitives[:, i]) > t:
                    return False
    return True

def find_k_anonimus(df):
    counts = dict()
    for row in df:
        if tuple(row.tolist()) in counts:
            counts[tuple(row.tolist())] += 1
        else:
            counts[tuple(row.tolist())] = 1

    min_k = 0
    for item in counts.items():
        min_k = item[1]
        break

    for _, count in counts.items():
        if count < min_k:
            min_k = count
    return min_k

def find_l_diverse(quasi_identifiers, sensitives):
    sensitive_values = dict()
    for identifiers, sensitive in zip(quasi_identifiers, sensitives):
        if tuple(identifiers.tolist()) in sensitive_values:
            sensitive_values[tuple(identifiers.tolist())].add(sensitive)
        else:
            sensitive_values[tuple(identifiers.tolist())] = set()
            sensitive_values[tuple(identifiers.tolist())].add(sensitive)
    min_l = -1
    for key in sensitive_values.keys():
        batch_sensitives = np.stack(list(sensitive_values[key]), axis=0)
        for i in range(batch_sensitives.shape[1]):
            cur_l = len(set(batch_sensitives[:, i].tolist()))
            if min_l == -1 or cur_l < min_l:
                min_l = cur_l
    return min_l

def find_t_close(quasi_identifiers, sensitives, sensitives_types, always_use_entropy = False):
    sensitive_values = dict()
    for identifiers, sensitive in zip(quasi_identifiers, sensitives):
        if tuple(identifiers.tolist()) in sensitive_values:
            sensitive_values[tuple(identifiers.tolist())].append(sensitive)
        else:
            sensitive_values[tuple(identifiers.tolist())] = list()
            sensitive_values[tuple(identifiers.tolist())].append(sensitive)
    max_t = 0
    for key in sensitive_values.keys():
        batch_sensitives = np.stack(list(sensitive_values[key]), axis=0)
        for i in range(batch_sensitives.shape[1]):
            if sensitives_types[i] == 'real' and not always_use_entropy:
                if real_sample_distance(sensitives[:, i], batch_sensitives[:, i]) > max_t:
                    max_t = real_sample_distance(sensitives[:, i], batch_sensitives[:, i])
            else:
                if categorical_sample_distance(sensitives[:, i], batch_sensitives[:, i]) > max_t:
                    max_t = categorical_sample_distance(sensitives[:, i], batch_sensitives[:, i])
    return max_t

def get_count_dict(l):
    count = dict()
    for el in l:
        if el in count:
            count[el] += 1
        else:
            count[el] = 1
    return count

def get_most_common_ken_from_count_dict(counts):
    most_common = -1
    for key in counts.keys():
        if most_common == -1 or counts[most_common] < counts[key]:
            most_common = key
    return most_common

def adversarial_knowledge_gain(depersonalized_qi, sensitives):
    s_count = get_count_dict(sensitives)

    s_set = set(s_count.keys())

    equivalence_classes_ids = dict()
    for i in range(depersonalized_qi.shape[0]):
        if tuple(depersonalized_qi[i].tolist()) not in equivalence_classes_ids:
            equivalence_classes_ids[tuple(depersonalized_qi[i].tolist())] = set()
            equivalence_classes_ids[tuple(depersonalized_qi[i].tolist())].add(i)
        else:
            equivalence_classes_ids[tuple(depersonalized_qi[i].tolist())].add(i)

    a_know = 0
    for class_key in equivalence_classes_ids.keys():
        a_diff = 0
        for s in s_set:
            s_class_count = 0
            for i in equivalence_classes_ids[class_key]:
                if sensitives[i] == s:
                    s_class_count += 1
            a_diff += abs(s_count[s] / len(sensitives) - s_class_count / len(equivalence_classes_ids[class_key]))
        a_diff /= 2
        a_know += a_diff * len(equivalence_classes_ids[class_key])
    a_know /= len(sensitives)
    return a_know

def adversarial_accuracy_gain(depersonalized_qi, sensitives):
    s_count = get_count_dict(sensitives)
    most_common_s = get_most_common_ken_from_count_dict(s_count)

    equivalence_classes_ids = dict()
    for i in range(depersonalized_qi.shape[0]):
        if tuple(depersonalized_qi[i].tolist()) not in equivalence_classes_ids:
            equivalence_classes_ids[tuple(depersonalized_qi[i].tolist())] = set()
            equivalence_classes_ids[tuple(depersonalized_qi[i].tolist())].add(i)
        else:
            equivalence_classes_ids[tuple(depersonalized_qi[i].tolist())].add(i)

    a_acc = -s_count[most_common_s] / len(sensitives)
    for class_key in equivalence_classes_ids.keys():
        s_count = get_count_dict([sensitives[i] for i in equivalence_classes_ids[class_key]])
        most_common_s = get_most_common_ken_from_count_dict(s_count)
        a_acc += s_count[most_common_s] / len(sensitives)

    return a_acc

def average_equivalence_class_size(qi):
    keys_set = set()
    for i in range(qi.shape[0]):
        keys_set.add(tuple(qi[i].tolist()))
    return qi.shape[0] / len(keys_set)

def distinctness(df):
    rows_set = set()
    for i in range(df.shape[0]):
        rows_set.add(tuple(df.iloc[i].tolist()))
    return len(rows_set) / df.shape[0]

def changed_proportion(initial_qi, qi):
    return (initial_qi != qi).sum()

def non_uniform_entropy(df):
    df_tuples = [tuple(df[i].tolist()) for i in range(df.shape[0])]
    elements_set = set(df_tuples)
    frequencies = get_elements_frequencies(df_tuples, elements_set)
    return entropy(frequencies, base=2)

def entropy_based_information_loss(initial_qi, qi):
    return 1 - non_uniform_entropy(qi) / non_uniform_entropy(initial_qi)

def my_by_element_distance_columns_unordered(initial_qi, qi):
    s = 0
    for i in range(qi.shape[0]):
        if is_nan(initial_qi[i]) + is_nan(qi[i]) == 1:
            s += 1
        if is_nan(initial_qi[i]) or is_nan(qi[i]):
            continue
        if not isinstance(qi[i], GeneralizationRange) and not isinstance(initial_qi[i], GeneralizationRange):
            s += qi[i] != initial_qi[i]
        elif not isinstance(qi[i], GeneralizationRange) and isinstance(initial_qi[i], GeneralizationRange):
            if qi[i] in initial_qi[i].values_set:
                s += 1 - 1 / len(initial_qi[i].values_set)
            else:
                s += 0
        elif isinstance(qi[i], GeneralizationRange) and not isinstance(initial_qi[i], GeneralizationRange):
            if initial_qi[i] in qi[i].values_set:
                s += 1 - 1 / len(qi[i].values_set)
            else:
                s += 0
        elif isinstance(qi[i], GeneralizationRange) and isinstance(initial_qi[i], GeneralizationRange):
            s += 1 - len(qi[i].values_set.intersection(initial_qi[i].values_set)) / len(qi[i].values_set.union(initial_qi[i].values_set))
    return s / qi.shape[0]

def my_by_element_distance_columns_ordered(initial_qi, qi):
    values_list = []
    for i in range(qi.shape[0]):
        if is_nan(initial_qi[i]):
            continue
        if isinstance(initial_qi[i], GeneralizationRange):
            values_list.append(initial_qi[i].mn)
            values_list.append(initial_qi[i].mx)
        else:
            values_list.append(initial_qi[i])
    values_list = sorted(values_list)
    ranks = dict()
    for i in range(len(values_list)):
        if values_list[i] not in ranks:
            ranks[values_list[i]] = i

    s = 0
    for i in range(qi.shape[0]):
        if is_nan(initial_qi[i]) + is_nan(qi[i]) == 1:
            s += 1
        if is_nan(initial_qi[i]) or is_nan(qi[i]):
            continue
        if not isinstance(qi[i], GeneralizationRange) and not isinstance(initial_qi[i], GeneralizationRange):
            s += abs(ranks[initial_qi[i]] - ranks[qi[i]]) / (qi.shape[0] - 1)
        elif not isinstance(qi[i], GeneralizationRange) and isinstance(initial_qi[i], GeneralizationRange):
            s += ((ranks[qi[i]] - ranks[initial_qi[i].min])**2 + (ranks[qi[i]] - ranks[initial_qi[i].max])**2) / (2 * (qi.shape[0] - 1) * (ranks[initial_qi[i].max] - ranks[initial_qi[i].min]))
        elif isinstance(qi[i], GeneralizationRange) and not isinstance(initial_qi[i], GeneralizationRange):
            s += ((ranks[qi[i].min] - ranks[initial_qi[i]])**2 + (ranks[qi[i].max] - ranks[initial_qi[i]])**2) / (2 * (qi.shape[0] - 1) * (ranks[qi[i].max] - ranks[qi[i].min]))
        #elif isinstance(qi[i], GeneralizationRange) and isinstance(initial_qi[i], GeneralizationRange):
        #    s += ((ranks[qi[i].min] - ranks[initial_qi[i].min])**2 + (ranks[qi[i].max] - ranks[initial_qi[i].max])**2) / (qi.shape[0] - 1)**2
    return s / qi.shape[0]

def my_by_element_distance_columns_real(initial_qi, qi):
    mn = np.min(initial_qi)
    mx = np.max(initial_qi)
    if mn == mx:
        return 0
    s = 0
    for i in range(qi.shape[0]):
        if is_nan(initial_qi[i]) + is_nan(qi[i]) == 1:
            s += 1
        if is_nan(initial_qi[i]) or is_nan(qi[i]):
            continue
        if not isinstance(qi[i], GeneralizationRange) and not isinstance(initial_qi[i], GeneralizationRange):
            s += abs(qi[i] - initial_qi[i]) / (mx - mn)
        elif not isinstance(qi[i], GeneralizationRange) and isinstance(initial_qi[i], GeneralizationRange):
            s += ((qi[i] - initial_qi[i].min) ** 2 + (qi[i] - initial_qi[i].max) ** 2) / (2 * (mx - mn) * (initial_qi[i].max - initial_qi[i].min))
        elif isinstance(qi[i], GeneralizationRange) and not isinstance(initial_qi[i], GeneralizationRange):
            s += ((initial_qi[i] - qi[i].min) ** 2 + (initial_qi[i] - qi[i].max) ** 2) / (2 * (mx - mn) * (qi[i].max - qi[i].min))
        #elif isinstance(qi[i], GeneralizationRange) and isinstance(initial_qi[i], GeneralizationRange):
        #    s += ((initial_qi[i].min - qi[i].min) ** 2 + (initial_qi[i].max - qi[i].max) ** 2) / (mx - mn) ** 2
    return s / qi.shape[0]

def my_by_element_distance(initial_qi, qi, column_types = None):
    if column_types is None:
        column_types = ['unordered'] * qi.shape[1]
    s = 0
    for i in range(qi.shape[1]):
        if column_types[i] == 'unordered':
            s += my_by_element_distance_columns_unordered(initial_qi[:, i], qi[:, i])
        elif column_types[i] == 'ordered':
            s += my_by_element_distance_columns_ordered(initial_qi[:, i], qi[:, i])
        elif column_types[i] == 'real':
            s += my_by_element_distance_columns_real(initial_qi[:, i], qi[:, i])
    return s / qi.shape[1]
