def group_by_dist(dists, group_size):
    grouped = [False] * len(dists)
    groups = []

    i = 0
    while i < len(dists):
        if grouped[i]:
            i += 1
            continue
        cur_dists = [(dists[i][j], j) for j in range(len(dists))]
        cur_dists.sort()
        group = []
        j = 0
        while len(group) < group_size and j < len(cur_dists):
            if not grouped[cur_dists[j][1]]:
                group.append(cur_dists[j][1])
                grouped[cur_dists[j][1]] = True
            j += 1
        if len(group) < group_size:
            groups[-1] = groups[-1] + group
        else:
            groups.append(group)
    return groups

def is_list_l_diverse(sens, l):
    if len(sens) == 0:
        return False
    column_values_sets = [set() for i in range(len(sens[0]))]
    for sn in sens:
        for i in range(len(sn)):
            column_values_sets[i].add(sn[i])
    for st in column_values_sets:
        if len(st) < l:
            return False
    return True

def group_by_dist_with_l_diverse(dists, sensitives, group_size, l):
    grouped = [False] * len(dists)
    groups = []

    i = 0
    while i < len(dists):
        if grouped[i]:
            i += 1
            continue
        i_dists = [(dists[i][j], j) for j in range(len(dists))]
        i_dists.sort()
        group = []
        group_sensitives = []
        j = 0
        while (len(group) < group_size or not is_list_l_diverse(group_sensitives, l)) and j < len(i_dists):
            if not grouped[i_dists[j][1]]:# and sensitives[j] not in group_sensitives:
                group.append(i_dists[j][1])
                grouped[i_dists[j][1]] = True
                group_sensitives.append(tuple(sensitives[j]))
            j += 1
        if len(group) < group_size or not is_list_l_diverse(group_sensitives, l):
            if len(groups) == 0:
                return None
            else:
                groups[-1] = groups[-1] + group
        else:
            groups.append(group)
    return groups