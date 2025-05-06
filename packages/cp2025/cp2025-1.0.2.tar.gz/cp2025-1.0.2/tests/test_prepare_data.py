from cp2025.utility.prepare_data import prepare_data
from numpy import genfromtxt
from sklearn.model_selection import train_test_split
import numpy as np
from cp2025.algorithms.GeneralizationKAnonymityTimeOptimal import GeneralizationKAnonymityTimeOptimal

df = genfromtxt('../data/Bank_Personal_Loan_Modelling.csv', delimiter=',')
df = np.delete(df, (0), axis=0)
df = np.delete(df, (0, 8, 9, 10, 11, 12, 13), axis=1)
print(df[0])
k = 2
#k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
k_anonymus_df, k_generalizations = GeneralizationKAnonymityTimeOptimal(k, 4 * ['real'] + ['unordered'] + ['real'] * 2).depersonalize(df)
print(k_anonymus_df[0])
train, test = train_test_split(k_anonymus_df, test_size=0.2, random_state=42)
new_train, new_test = prepare_data(train, test, [1] * train.shape[1], 4 * ['real'] + ['unordered'] + ['real'] * 2)
print(new_train[0])
#sdf, n_sup = AggregationGreedyByOneEqualSizedGroups(2, ['real']*7).depersonalize(df)
