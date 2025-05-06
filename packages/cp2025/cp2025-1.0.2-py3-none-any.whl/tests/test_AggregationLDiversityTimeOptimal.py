import unittest
import numpy as np
import random
from cp2025.algorithms.AggregationLDiversityTimeOptimal import AggregationLDiversityTimeOptimal
from UnorderedClass import UnorderedClass

class TestGeneralizationLDiversityTimeOptimal(unittest.TestCase):

    def test_initially_k_anonymus(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 1],
        ]
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, l_diverse_df)
        self.assertEqual(k_replaced, 0)

    def test_generalize_last_element(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 3, 1],
        ]
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(k_replaced, 2)

    def test_generalize_everything(self):
        df = [
            [1, 1, 1, 1, 1],
            [2, 2, 2, 2, 1],
            [3, 3, 3, 3, 1],
            [4, 4, 4, 4, 2],
        ]
        k = 4
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[4])
        general_df = [[2.5] * 4 + [1] for i in range(4)]
        general_df[3][4] = 2
        self.assertEqual(l_diverse_df, general_df)
        self.assertEqual(k_replaced, 16)

    def test_big_k(self):
        df = [
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 1, 2],
            [1, 1, 1, 2, 1, 2],
            [1, 1, 1, 1, 1, 1],
        ]
        k = 5
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[3, 5])
        self.assertEqual(l_diverse_df, [[1, 1], [2, 2], [2, 2], [1, 1]])
        self.assertEqual(k_replaced, None)

    def test_k_equals_one(self):
        df = [
            [1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2],
            [3, 3, 3, 3, 2],
            [4, 4, 4, 4, 1],
        ]
        k = 1
        l = 1
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(l_diverse_df, df)
        self.assertEqual(k_replaced, 0)

    def test_numpy(self):
        df = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 1],
        ]
        df = np.array(df)
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[4])
        self.assertTrue((df == l_diverse_df).all())
        self.assertEqual(k_replaced, 0)

    def test_string_data(self):
        df = [
            ["a", "a", "a", "a", 1],
            ["a", "a", "a", "a", 2],
            ["b", "b", "b", "b", 2],
            ["b", "b", "b", "b", 1],
        ]
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['ordered']*4).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, l_diverse_df)
        self.assertEqual(k_replaced, 0)

    def test_float_data(self):
        df = [
            [1.0, 1.0, 1.0, 1.0, 1],
            [1.0, 1.0, 1.0, 1.0, 2],
            [2.0, 2.0, 2.0, 2.0, 2],
            [2.0, 2.0, 2.0, 2.0, 1],
        ]
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real']*4).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, l_diverse_df)
        self.assertEqual(k_replaced, 0)

    def test_mixed_data(self):
        df = [
            [1.0, 1.0, "a", 1, 1],
            [1.0, 1.0, "a", 1, 2],
            [2.0, 2.0, "b", 2, 2],
            [2.0, 2.0, "b", 2, 1],
        ]
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['real', 'real', 'ordered', 'real']).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df, l_diverse_df)
        self.assertEqual(k_replaced, 0)

    def test_truly_unordered(self):
        df = [
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), 1],
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), 2],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), 1],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), 1],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(3), 2],
        ]
        df_expected = [
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), 1],
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), 2],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), 1],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), 1],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), 2],
        ]
        k = 2
        l = 2
        l_diverse_df, k_replaced = AggregationLDiversityTimeOptimal(k, l, ['unordered'] * 4).depersonalize(df, sensitives_ids=[4])
        self.assertEqual(df_expected, l_diverse_df)
        self.assertEqual(k_replaced, 1)

    def test_random_df(self):
        seed = 1234
        random.seed(seed)
        np.random.seed(seed)
        for i in range(1000):
            rows = random.randint(4, 50)
            cols = random.randint(2, 6)
            df = np.random.randint(0, 3, (rows, cols))
            k = random.randint(2, 4)
            l = random.randint(2, k)
            k_sens = random.randint(1, cols-1)
            quasi_identifiers_types = []
            for j in range(cols):
                quasi_identifiers_types.append(random.choice(['real', 'ordered', 'unordered']))
            l_diverse_df, k_replaced = (AggregationLDiversityTimeOptimal(k, l, quasi_identifiers_types=quasi_identifiers_types)
                                                .depersonalize(df, sensitives_ids=list(range(k_sens))))



if __name__ == '__main__':
    unittest.main()
