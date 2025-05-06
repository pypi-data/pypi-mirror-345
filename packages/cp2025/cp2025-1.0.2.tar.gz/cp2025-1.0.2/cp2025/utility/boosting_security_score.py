from sklearn.ensemble import GradientBoostingClassifier
import numpy as np
import random

def get_boosting_security_score(train, train_depersonalized, test, test_depersonalized):
    similar_train = np.concatenate((train, train_depersonalized), axis=1)
    different_train_depersonalized = np.zeros(train_depersonalized.shape)
    new_y = np.zeros(2 * train.shape[0])
    for i in range(train.shape[0]):
        shift = random.randint(1, train.shape[0] - 1)
        different_train_depersonalized[i, :] = train_depersonalized[(i + shift) % train.shape[0], :]
        new_y[i + train.shape[0]] = 1
    different_train = np.concatenate((train, different_train_depersonalized), axis=1)
    boosting_train = np.concatenate((similar_train, different_train), axis=0)

    clf = GradientBoostingClassifier(random_state=0, n_estimators=1000)
    clf.fit(boosting_train, new_y)

    correct_count = 0
    for i in range(test.shape[0]):
        copied_object = np.zeros(test_depersonalized.shape)
        for j in range(test_depersonalized.shape[0]):
            copied_object[j] = test_depersonalized[i]
        x = np.concatenate((test, copied_object), axis=1)
        probs = clf.predict_proba(x)
        max_prob_id = 0
        for j in range(test.shape[0]):
            if probs[j, 0] > probs[max_prob_id, 0]:
                max_prob_id = j
        if max_prob_id == i:
            correct_count += 1

    return correct_count / test.shape[0]