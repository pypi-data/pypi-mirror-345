import unittest
import numpy as np
from cp2025.algorithms.SuppressionTClosenessBaseline import SuppressionTClosenessBaseline

class TestSuppressionTClosenessBaseline(unittest.TestCase):

    def test_initially_t_close(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 1],
        ]
        k = 2
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, t_close_df)
        self.assertEqual(k_suppressions, 0)

    def test_suppress_last_element(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 3, 1],
        ]
        k = 2
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(k_suppressions, 2)

    def test_suppress_everything(self):
        df = [
            [1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
        ]
        k = 1
        t = 1e-5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        none_df = [
            [np.nan, np.nan, np.nan, np.nan, 1],
            [np.nan, np.nan, np.nan, np.nan, 2],
            [np.nan, np.nan, np.nan, np.nan, 3],
            [np.nan, np.nan, np.nan, np.nan, 4],
        ]
        self.assertEqual(t_close_df, none_df)
        self.assertEqual(k_suppressions, 16)

    def test_big_k(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [1, 1, 1, 1, 2],
            [1, 1, 1, 1, 1],
        ]
        k = 5
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(t_close_df, [[1], [2], [2], [1]])
        self.assertEqual(k_suppressions, None)

    def test_k_equals_one(self):
        df = [
            [1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2],
            [3, 3, 3, 3, 2],
            [4, 4, 4, 4, 1],
        ]
        k = 1
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(t_close_df, df)
        self.assertEqual(k_suppressions, 0)

    def test_numpy(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 1],
        ]
        df = np.array(df)
        k = 2
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertTrue((df == t_close_df).all())
        self.assertEqual(k_suppressions, 0)

    def test_string_data(self):
        df = [
            ["a", "a", "a", "a", 1],
            ["a", "a", "a", "a", 2],
            ["b", "b", "b", "b", 2],
            ["b", "b", "b", "b", 1],
        ]
        k = 2
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, t_close_df)
        self.assertEqual(k_suppressions, 0)

    def test_float_data(self):
        df = [
            [1.0, 1.0, 1.0, 1.0, 1],
            [1.0, 1.0, 1.0, 1.0, 2],
            [2.0, 2.0, 2.0, 2.0, 2],
            [2.0, 2.0, 2.0, 2.0, 1],
        ]
        k = 2
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, t_close_df)
        self.assertEqual(k_suppressions, 0)

    def test_mixed_data(self):
        df = [
            [1.0, 1.0, "a", 1, 1],
            [1.0, 1.0, "a", 1, 2],
            [2.0, 2.0, "b", 2, 2],
            [2.0, 2.0, "b", 2, 1],
        ]
        k = 2
        t = 0.5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, t_close_df)
        self.assertEqual(k_suppressions, 0)

    def test_string_sensitive(self):
        df = [
            [1, 1, 1, 1, 'a'],
            [2, 2, 2, 2, 'b'],
            [3, 3, 3, 3, 'c'],
            [4, 4, 4, 4, 'd'],
        ]
        k = 1
        t = 1e-5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['unordered']).depersonalize(df, sensitives_ids=[4])
        none_df = [
            [np.nan, np.nan, np.nan, np.nan, 'a'],
            [np.nan, np.nan, np.nan, np.nan, 'b'],
            [np.nan, np.nan, np.nan, np.nan, 'c'],
            [np.nan, np.nan, np.nan, np.nan, 'd'],
        ]
        self.assertEqual(t_close_df, none_df)
        self.assertEqual(k_suppressions, 16)

    def test_mixed_sensitives(self):
        df = [
            [1, 1, 1, 1, 'a', 1],
            [2, 2, 2, 2, 'b', 2],
            [3, 3, 3, 3, 'c', 3],
            [4, 4, 4, 4, 'd', 4],
        ]
        k = 1
        t = 1e-5
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['unordered', 'real']).depersonalize(df, sensitives_ids=[4, 5])
        none_df = [
            [np.nan, np.nan, np.nan, np.nan, 'a', 1],
            [np.nan, np.nan, np.nan, np.nan, 'b', 2],
            [np.nan, np.nan, np.nan, np.nan, 'c', 3],
            [np.nan, np.nan, np.nan, np.nan, 'd', 4],
        ]
        self.assertEqual(t_close_df, none_df)
        self.assertEqual(k_suppressions, 16)

    def test_t_closeness_real_case_1(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 2, 2],
            [1, 1, 1, 3, 3],
            [1, 4, 4, 4, 1],
            [1, 4, 4, 5, 2],
        ]
        k = 2
        t = 0.15
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df,sensitives_ids=[4])
        correct_t_close_df = [
            [1, 1, 1, np.nan, 1],
            [1, 1, 1, np.nan, 2],
            [1, 1, 1, np.nan, 3],
            [1, 4, 4, np.nan, 1],
            [1, 4, 4, np.nan, 2],
        ]
        self.assertEqual(t_close_df, correct_t_close_df)
        self.assertEqual(k_suppressions, 5)

    def test_t_closeness_real_case_2(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 2, 2],
            [1, 1, 1, 3, 3],
            [1, 4, 4, 4, 1],
            [1, 4, 4, 5, 2],
        ]
        k = 2
        t = 0.14
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['real']).depersonalize(df,sensitives_ids=[4])
        correct_t_close_df = [
            [1, np.nan, np.nan, np.nan, 1],
            [1, np.nan, np.nan, np.nan, 2],
            [1, np.nan, np.nan, np.nan, 3],
            [1, np.nan, np.nan, np.nan, 1],
            [1, np.nan, np.nan, np.nan, 2],
        ]
        self.assertEqual(t_close_df, correct_t_close_df)
        self.assertEqual(k_suppressions, 15)

    def test_t_closeness_categorical_case_1(self):
        df = [
            [1, 1, 1, 1, 'a'],
            [1, 1, 1, 2, 'b'],
            [1, 1, 1, 3, 'c'],
            [1, 4, 4, 4, 'a'],
            [1, 4, 4, 5, 'b'],
        ]
        k = 2
        t = 0.075
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['unordered']).depersonalize(df,sensitives_ids=[4])
        correct_t_close_df = [
            [1, 1, 1, np.nan, 'a'],
            [1, 1, 1, np.nan, 'b'],
            [1, 1, 1, np.nan, 'c'],
            [1, 4, 4, np.nan, 'a'],
            [1, 4, 4, np.nan, 'b'],
        ]
        self.assertEqual(t_close_df, correct_t_close_df)
        self.assertEqual(k_suppressions, 5)

    def test_t_closeness_categorical_case_2(self):
        df = [
            [1, 1, 1, 1, 'a'],
            [1, 1, 1, 2, 'b'],
            [1, 1, 1, 3, 'c'],
            [1, 4, 4, 4, 'a'],
            [1, 4, 4, 5, 'b'],
        ]
        k = 2
        t = 0.07
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['unordered']).depersonalize(df,sensitives_ids=[4])
        correct_t_close_df = [
            [1, np.nan, np.nan, np.nan, 'a'],
            [1, np.nan, np.nan, np.nan, 'b'],
            [1, np.nan, np.nan, np.nan, 'c'],
            [1, np.nan, np.nan, np.nan, 'a'],
            [1, np.nan, np.nan, np.nan, 'b'],
        ]
        self.assertEqual(t_close_df, correct_t_close_df)
        self.assertEqual(k_suppressions, 15)



if __name__ == '__main__':
    unittest.main()
