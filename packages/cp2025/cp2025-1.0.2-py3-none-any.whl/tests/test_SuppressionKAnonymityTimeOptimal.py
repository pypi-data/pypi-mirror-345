import unittest
import numpy as np
import random
from cp2025.algorithms.SuppressionKAnonymityTimeOptimal import SuppressionKAnonymityTimeOptimal

class TestSuppressionKAnonymityTimeOptimal(unittest.TestCase):

    def test_initially_k_anonymus(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_suppressions, 0)

    def test_suppress_last_element(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 3],
        ]
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(k_suppressions, 2)

    def test_suppress_everything(self):
        df = [
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [4, 4, 4, 4],
        ]
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        none_df = [
            [np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan],
        ]
        self.assertEqual(k_anonymus_df, none_df)
        self.assertEqual(k_suppressions, 16)

    def test_big_k(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
        ]
        k = 5
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(k_anonymus_df, None)
        self.assertEqual(k_suppressions, None)

    def test_k_equals_one(self):
        df = [
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [4, 4, 4, 4],
        ]
        k = 1
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(k_anonymus_df, df)
        self.assertEqual(k_suppressions, 0)

    def test_numpy(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        df = np.array(df)
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertTrue((df == k_anonymus_df).all())
        self.assertEqual(k_suppressions, 0)

    def test_string_data(self):
        df = [
            ["a", "a", "a", "a"],
            ["a", "a", "a", "a"],
            ["b", "b", "b", "b"],
            ["b", "b", "b", "b"],
        ]
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_suppressions, 0)

    def test_float_data(self):
        df = [
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [2.0, 2.0, 2.0, 2.0],
            [2.0, 2.0, 2.0, 2.0],
        ]
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_suppressions, 0)

    def test_mixed_data(self):
        df = [
            [1.0, 1.0, "a", 1],
            [1.0, 1.0, "a", 1],
            [2.0, 2.0, "b", 2],
            [2.0, 2.0, "b", 2],
        ]
        k = 2
        k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_suppressions, 0)

    def test_random_df(self):
        seed = 1234
        random.seed(seed)
        np.random.seed(seed)
        for i in range(1000):
            rows = random.randint(4, 50)
            cols = random.randint(1, 5)
            df = np.random.randint(0, 3, (rows, cols))
            k = random.randint(2, 4)
            k_anonymus_df, k_suppressions = SuppressionKAnonymityTimeOptimal(k).depersonalize(df)

if __name__ == '__main__':
    unittest.main()
