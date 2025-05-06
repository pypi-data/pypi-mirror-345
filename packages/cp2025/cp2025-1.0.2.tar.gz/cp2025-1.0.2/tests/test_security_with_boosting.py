from cp2025.utility.prepare_data import prepare_data
from numpy import genfromtxt
from sklearn.model_selection import train_test_split
import numpy as np
from cp2025.algorithms.RandomizationDepersonalizator import RandomizationBaselineDepersonalizator
from cp2025.utility.boosting_security_score import get_boosting_security_score

df = genfromtxt('../data/Bank_Personal_Loan_Modelling.csv', delimiter=',')

df = np.delete(df, (0), axis=0)
df_copy = np.copy(df)
df = np.delete(df, (0, 8, 9, 10, 11, 12, 13), axis=1)

k = 2
scale = 0.1
train_initial, test_initial = train_test_split(df, test_size=0.2, random_state=42, shuffle=False)
#train, k_generalizations_train = GeneralizationKAnonymityTimeOptimal(k, 7 * ['real']).depersonalize(train_initial)
#test, k_generalizations_test = GeneralizationKAnonymityTimeOptimal(k, 7 * ['real']).depersonalize(test_initial)
train = RandomizationBaselineDepersonalizator(quasi_identifiers_types=['real']*7, scale = scale).depersonalize(train_initial)[0]
test = RandomizationBaselineDepersonalizator(quasi_identifiers_types=['real']*7, scale = scale).depersonalize(test_initial)[0]

#train, test = train_test_split(k_anonymus_df, test_size=0.2, random_state=42, shuffle=False)

new_train, new_test = prepare_data(train, test, [1] * train.shape[1], 8 * ['real'], normalize=False)

print(get_boosting_security_score(train_initial, new_train, test_initial, new_test))

'''similar_train = np.concatenate((train_initial, new_train), axis=1)
different_new_train = np.zeros(new_train.shape)
new_y = np.zeros(2 * train_initial.shape[0])
for i in range(train_initial.shape[0]):
    shift = random.randint(1, train_initial.shape[0] - 1)
    different_new_train[i, :] = new_train[(i+shift) % train_initial.shape[0], :]
    new_y[i + train_initial.shape[0]] = 1
different_train = np.concatenate((train_initial, different_new_train), axis=1)
new_train_c = np.concatenate((similar_train, different_train), axis=0)

clf = GradientBoostingClassifier(random_state=0, n_estimators=1000)
clf.fit(new_train_c, new_y)

correct_count = 0
for i in range(test_initial.shape[0]):
    copied_object = np.zeros(new_test.shape)
    for j in range(new_test.shape[0]):
        copied_object[j] = new_test[i]
    x = np.concatenate((test_initial, copied_object), axis=1)
    probs = clf.predict_proba(x)#model(torch.from_numpy(x.astype(float)).float())
    max_prob_id = 0
    for j in range(test_initial.shape[0]):
        if probs[j, 0] > probs[max_prob_id, 0]:
            max_prob_id = j
    if max_prob_id == i:
        correct_count += 1
print(correct_count / test_initial.shape[0])'''


'''similar_test = np.concatenate((test_initial, new_test), axis=1)
different_new_test = np.zeros(new_test.shape)
new_y = np.zeros(2 * test_initial.shape[0])
for i in range(test_initial.shape[0]):
    shift = random.randint(1, test_initial.shape[0] - 1)
    different_new_test[i, :] = new_test[(i+shift) % test_initial.shape[0], :]
    new_y[i + test_initial.shape[0]] = 1
different_test = np.concatenate((test_initial, different_new_test), axis=1)
#new_test = np.concatenate((different_new_test, different_new_test), axis=0)

#print(clf.predict_proba(new_test))
#print(clf.score(new_test, new_y))'''


'''import torch
from torch import nn
from torch.utils.data import Dataset
import torch.nn.functional as F

device = 'cpu'
model = nn.Sequential(
    nn.Linear(new_train_c.shape[1], 5),
    nn.BatchNorm1d(5),
    nn.ReLU(),
    nn.Linear(5, 5),
    nn.BatchNorm1d(5),
    nn.ReLU(),
    nn.Linear(5, 2),
)
train_set = torch.utils.data.TensorDataset(torch.from_numpy(new_train_c.astype(float)), torch.from_numpy(new_y))
train_loader = torch.utils.data.DataLoader(train_set, batch_size=32, shuffle=True)
optimizer = torch.optim.SGD(model.parameters(), lr=1e-1)
criterion = F.cross_entropy
n_epoch=100
for i in range(n_epoch):
    model.train()
    for x_batch, y_batch in train_loader:
        x_batch = x_batch.to(device).float()
        y_batch = y_batch.to(device).long()

        output = model(x_batch)
        loss = criterion(output, y_batch)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()'''


'''correct_count = 0
for i in range(train_initial.shape[0]):
    copied_object = np.zeros(new_train.shape)
    for j in range(new_train.shape[0]):
        copied_object[j] = new_train[i]
    x = np.concatenate((train_initial, copied_object), axis=1)
    probs = clf.predict_proba(x)#model(torch.from_numpy(x.astype(float)).float())
    max_prob_id = 0
    for j in range(train_initial.shape[0]):
        if probs[j, 0] > probs[max_prob_id, 0]:
            max_prob_id = j
    if max_prob_id == i:
        correct_count += 1
print(correct_count / train_initial.shape[0])'''

