from sklearn.ensemble import GradientBoostingRegressor
from cp2025.utility.prepare_data import prepare_data
from numpy import genfromtxt
from sklearn.model_selection import train_test_split
import numpy as np
from cp2025.algorithms.GeneralizationKAnonymityTimeOptimal import GeneralizationKAnonymityTimeOptimal
from sklearn.model_selection import GridSearchCV

df = genfromtxt('../data/Bank_Personal_Loan_Modelling.csv', delimiter=',')

df = np.delete(df, (0), axis=0)
df_copy = np.copy(df)
y = df_copy[:,8]
df = np.delete(df, (0, 8, 9, 10, 11, 12, 13), axis=1)

k = 5
k_anonymus_df, k_generalizations = GeneralizationKAnonymityTimeOptimal(k, 7 * ['real']).depersonalize(df)

train, test, y_train, y_test = train_test_split(k_anonymus_df, y, test_size=0.2, random_state=42)
new_train, new_test = prepare_data(train, test, [1] * train.shape[1], 7 * ['real'])

parameters = {
    'n_estimators':list(range(10, 201, 15)),
    #'alpha':[i / 10 for i in range(1, 10, 4)],
    'min_samples_leaf':[i for i in range(1, 6)],
    'criterion':['squared_error'],
}

reg = GridSearchCV(GradientBoostingRegressor(random_state=0), parameters)
reg.fit(new_train, y_train)
res = reg.predict(new_test)
print(((res - y_test)**2).mean()**0.5)

train, test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)
train, test = prepare_data(train, test, [1] * train.shape[1], 7 * ['real'])
reg =GridSearchCV(GradientBoostingRegressor(random_state=0), parameters)
reg.fit(train, y_train)
res = reg.predict(test)
print(((res - y_test)**2).mean()**0.5)
