import unittest
import numpy as np
from cp2025.utility.metrics import adversarial_accuracy_gain


class TestAdversarialAccuracyGain(unittest.TestCase):

    def test_normal(self):
        qi = np.array([[1], [1], [1], [2], [2], [2]])
        sensitives = np.array([1, 1, 3, 1, 2, 2])

        score = adversarial_accuracy_gain(qi, sensitives)

        assert abs(1/6 - score) < 1e-5

    def test_equal_qi(self):
        qi = np.array([[1], [1], [1], [1], [1], [1]])
        sensitives = np.array([1, 1, 3, 1, 2, 2])

        score = adversarial_accuracy_gain(qi, sensitives)

        assert abs(score) < 1e-5

    def test_equal_sensitives(self):
        qi = np.array([[1], [1], [1], [2], [2], [2]])
        sensitives = np.array([1, 1, 1, 1, 1, 1])

        score = adversarial_accuracy_gain(qi, sensitives)

        assert abs(score) < 1e-5

    def test_all_equal(self):
        qi = np.array([[1], [1], [1], [1], [1], [1]])
        sensitives = np.array([1, 1, 1, 1, 1, 1])

        score = adversarial_accuracy_gain(qi, sensitives)

        assert abs(score) < 1e-5

if __name__ == '__main__':
    unittest.main()
