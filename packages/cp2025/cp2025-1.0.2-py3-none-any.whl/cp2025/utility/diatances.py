import numpy as np

def dfs_hamming_distances(df):
    return dfs_rank_general_dist(df, ['unordered'] * len(df[0]))

def dfs_rank_distances(df):
    return dfs_rank_general_dist(df, ['ordered'] * len(df[0]))

def dfs_rank_general_dist(df, value_classes):
    sorted_columns = []
    for i in range(len(df[0])):
        if value_classes[i] != 'unordered':
            sorted_columns.append(sorted(df[:, i].tolist()))
        else:
            sorted_columns.append(df[:, i].tolist())

    ranks = []
    for i in range(len(df[0])):
        if value_classes[i] == 'real':
            ranks.append(None)
            continue
        if value_classes[i] == 'unordered':
            ranks.append(None)
            continue
        rng = dict()
        for j in range(len(sorted_columns[i])):
            if sorted_columns[i][j] not in rng:
                rng[sorted_columns[i][j]] = j
        ranks.append(rng)

    df_mins = [None] * len(df[0])  # Rewrite in numpy
    df_maxs = [None] * len(df[0])
    for i in range(len(df[0])):
        if value_classes[i] != 'real':
            continue
        for j in range(len(df)):
            if df_mins[i] is None or df_mins[i] > df[j][i]:
                df_mins[i] = df[j][i]
            if df_maxs[i] is None or df_maxs[i] < df[j][i]:
                df_maxs[i] = df[j][i]

    df_values_dists = np.zeros((len(df), len(df[0])))
    df_unordered_values = np.zeros((len(df), len(df[0])), dtype=object)
    for i in range(len(df)):
        for j in range(len(df[0])):
            if value_classes[j] == 'real':
                df_values_dists[i][j] = 0 if df_maxs[j] == df_mins[j] or df_maxs[j] is None or df_mins[j] is None\
                    else (df[i][j] - df_mins[j]) / (df_maxs[j] - df_mins[j])
            elif value_classes[j] == 'ordered':
                df_values_dists[i][j] = ranks[j][df[i][j]] / len(df)
            elif value_classes[j] == 'unordered':
                df_unordered_values[i][j] = df[i][j]

    my_dist = np.zeros((len(df), len(df)))
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            dist = np.abs(df_values_dists[i] - df_values_dists[j]).sum() + (df_unordered_values[i] != df_unordered_values[j]).sum()
            my_dist[i][j] = dist
            my_dist[j][i] = dist

    return my_dist