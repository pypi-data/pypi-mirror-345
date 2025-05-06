from numpy import genfromtxt
import numpy as np
from cp2025.algorithms.SuppressionKAnonymityTimeOptimal import SuppressionKAnonymityTimeOptimal
from cp2025.algorithms.Datafly import Datafly
from cp2025.algorithms.GeneralizationGreedyByOneEqualSizedGroups import GeneralizationGreedyByOneEqualSizedGroups
from cp2025.algorithms.GeneralizationKAnonymityTimeOptimal import GeneralizationKAnonymityTimeOptimal
from cp2025.algorithms.GeneralizationKAnonymityGroupJoin import GeneralizationKAnonymityGroupJoin
from cp2025.algorithms.SuppressionKAnonymityTimeOptimal import SuppressionKAnonymityTimeOptimal
from cp2025.utility.metrics import my_by_element_distance
from cp2025.algorithms.groupjoin import GroupJoinAggregation, GroupJoinDepersonalizator, GroupJoinTCloseness
from cp2025.algorithms.DistributedDataKAnonymityDepersonalization import DistributedDataOwnerKAnonymityDepersonalizator

df = genfromtxt('../data/Bank_Personal_Loan_Modelling.csv', delimiter=',')
df = np.delete(df, (0), axis=0)
df = np.delete(df, (0, 8, 9, 10, 11, 12, 13), axis=1)
'''gjmth = GroupJoinAggregation(['real']*6)
gjmtc = GroupJoinTCloseness(2, 1, ['real'], always_use_entropy=True)
dep = GroupJoinDepersonalizator(gjmth, gjmtc)'''
#sdf, n_sup = Datafly(2, ['real']*7, k_suppressed_lines=500).depersonalize(df)
#sdf, n_sup = GeneralizationKAnonymityGroupJoin(2, 4 * ['real'] + ['unordered'] + ['real'] * 2).depersonalize(df)
#sdf, n_sup = dep.depersonalize(df, sensitives_ids=[4])
#sdf, n_sup = SuppressionKAnonymityTimeOptimal(k=2).depersonalize(df)
#print(sdf[0:5])
#print(n_sup)
dep1 = DistributedDataOwnerKAnonymityDepersonalizator(df[:,:4], np.array([]), 2, 7, seed=7,
                                                      quasi_identifiers_types=['real'] * df[:,:4].shape[1])
dep2 = DistributedDataOwnerKAnonymityDepersonalizator(df[:,4:], np.array([]), 2, 8, seed=7,
                                                      quasi_identifiers_types=['real'] * df[:,4:].shape[1])
dep1.set_other_data_owner(dep2)
dep2.set_other_data_owner(dep1)
dep1.exchange_data()
print(dep1.joined_data[:5])
'''for i in range(len(sdf)):
    if sdf[i][0] is None:
        sdf[i] = df[0]
for i in range(7):
    print(i, len(np.unique(sdf[:,i])), len(np.unique(df[:,i])))'''
#print("Distance initial-depersonalized:", my_by_element_distance(df, sdf, 4 * ['real'] + ['real'] + ['real'] * 2))


