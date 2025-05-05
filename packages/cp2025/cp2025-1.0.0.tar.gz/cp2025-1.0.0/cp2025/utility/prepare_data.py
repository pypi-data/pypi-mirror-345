from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
import numpy as np
from cp2025.utility.GeneralizationRange import GeneralizationRange
import pandas as pd
from statistics import mode

def fill_nulls(train, test, column_type = 'unordered'):
    value = np.nan
    if column_type == 'unordered':
        value = mode(train[~pd.isna(train)])
    if column_type == 'ordered':
        value = np.median(train[~pd.isna(train)])
    if column_type == 'real':
        value = np.mean(train[~pd.isna(train)])

    train[pd.isna(train)] = value
    test[pd.isna(test)] = value

    return train, test

def is_nan(value):
    try:
        if value is None:
            return True
        res = np.isnan(value)
        return res
    except:
        return False

def transform_ordered_ranges(train, test):
    new_train = np.zeros((train.shape[0], 2))
    for i in range(train.shape[0]):
        if is_nan(train[i]):
            new_train[i, 0] = np.nan
            new_train[i, 1] = np.nan
        elif isinstance(train[i], GeneralizationRange):
            new_train[i, 0] = train[i].min
            new_train[i, 1] = train[i].max
        else:
            new_train[i, 0] = train[i]
            new_train[i, 1] = train[i]

    new_test = np.zeros((test.shape[0], 2))
    for i in range(test.shape[0]):
        if is_nan(test[i]):
            new_test[i, 0] = np.nan
            new_test[i, 1] = np.nan
        elif isinstance(test[i], GeneralizationRange):
            new_test[i, 0] = test[i].min
            new_test[i, 1] = test[i].max
        else:
            new_test[i, 0] = test[i]
            new_test[i, 1] = test[i]

    mn = np.min(new_train[:, 0][~pd.isna(new_train[:, 0])])
    new_train[:, 0][pd.isna(new_train[:, 0])] = mn
    new_test[:, 0][pd.isna(new_test[:, 0])] = mn
    mx = np.max(new_train[:, 1][~pd.isna(new_train[:, 1])])
    new_train[:, 1][pd.isna(new_train[:, 1])] = mx
    new_test[:, 1][pd.isna(new_test[:, 1])] = mx

    return new_train, new_test

def transform_unordered_ranges(train, test):
    unique_values = set()
    for el in train:
        if is_nan(el):
            pass
        elif isinstance(el, GeneralizationRange):
            unique_values.update(el.values_set)
        else:
            unique_values.add(el)
    unique_values = list(unique_values)
    new_train = np.zeros((train.shape[0], len(unique_values)))
    for i in range(train.shape[0]):
        if is_nan(train[i]):
            pass
        elif isinstance(train[i], GeneralizationRange):
            value = 1 / len(train[i].values_set)
            for el in train[i].values_set:
                new_train[i, unique_values.index(el)] = value
        else:
            new_train[i, unique_values.index(train[i])] = 1

    new_test = np.zeros((test.shape[0], len(unique_values)))
    for i in range(test.shape[0]):
        if is_nan(test[i]):
            pass
        elif isinstance(test[i], GeneralizationRange):
            value = 1 / len(test[i].values_set)
            for el in test[i].values_set:
                if el in unique_values:
                    new_test[i, unique_values.index(el)] = value
        else:
            if test[i] in unique_values:
                new_test[i, unique_values.index(test[i])] = 1

    return new_train, new_test

def ohe_all(train, test, cols_to_ohe_ids):
    ohe = OneHotEncoder(
        sparse_output=False,
        handle_unknown='ignore',
    )

    cols_number = train.shape[1]
    cols_not_to_ohe_ids = []
    for col in range(cols_number):
        if col not in cols_to_ohe_ids:
            cols_not_to_ohe_ids.append(col)
    cols_to_ohe_train = train[:, cols_to_ohe_ids]
    cols_to_ohe_test = test[:, cols_to_ohe_ids]
    cols_not_to_ohe_train = train[:, cols_not_to_ohe_ids]
    cols_not_to_ohe_test = test[:, cols_not_to_ohe_ids]

    cols_to_ohe_train_transformed = ohe.fit_transform(cols_to_ohe_train)
    cols_to_ohe_test_transformed = ohe.transform(cols_to_ohe_test)

    return np.column_stack((cols_to_ohe_train_transformed, cols_not_to_ohe_train)), np.column_stack((cols_not_to_ohe_test, cols_to_ohe_test_transformed))

def prepare_data(train, test, has_ranges, column_types, normalize = True):
    cols_to_ohe_ids = []
    train_cols_to_stack = []
    test_cols_to_stack = []
    for i in range(train.shape[1]):
        if not has_ranges[i]:
            train_col, test_col = fill_nulls(train[:,i], test[:,i], column_types[i])
            train_cols_to_stack.append(train_col)
            test_cols_to_stack.append(test_col)
            if column_types[i] in ['ordered', 'unordered']:
                cols_to_ohe_ids.append(len(train_cols_to_stack)-1)
        else:
            if column_types[i] == 'unordered':
                train_col, test_col = transform_unordered_ranges(train[:,i], test[:,i])
            else:
                train_col, test_col = transform_ordered_ranges(train[:,i], test[:,i])
            for j in range(train_col.shape[1]):
                train_cols_to_stack.append(train_col[:,j])
                test_cols_to_stack.append(test_col[:,j])
                if column_types[i] in ['ordered']:
                    cols_to_ohe_ids.append(len(train_cols_to_stack) - 1)

    new_train = np.column_stack(train_cols_to_stack)
    new_test = np.column_stack(test_cols_to_stack)

    if len(cols_to_ohe_ids) > 0:
        new_train, new_test = ohe_all(new_train, new_test, cols_to_ohe_ids)

    if normalize:
        scaler = StandardScaler()
        new_train = scaler.fit_transform(new_train)
        new_test = scaler.transform(new_test)

    return new_train, new_test
