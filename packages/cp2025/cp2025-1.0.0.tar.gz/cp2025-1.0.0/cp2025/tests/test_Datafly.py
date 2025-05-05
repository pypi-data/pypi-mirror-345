import unittest
import numpy as np
import random
from cp2025.algorithms.Datafly import Datafly
from UnorderedClass import UnorderedClass
from cp2025.utility.GeneralizationRange import GeneralizationRange

class TestDatafly(unittest.TestCase):

    def test_initially_k_anonymus(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_changes, 0)

    def test_generalize_last_element(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 3],
        ]
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertEqual(k_changes, 2)

    def test_truly_unordered(self):
        df = [
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1)],
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1)],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(2)],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), UnorderedClass(3)],
        ]
        generalized_value = GeneralizationRange(column_type='unordered', column_values=np.array([UnorderedClass(2), UnorderedClass(3)]))
        df_expected = [
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1)],
            [UnorderedClass(1), UnorderedClass(1), UnorderedClass(1), UnorderedClass(1)],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), generalized_value],
            [UnorderedClass(2), UnorderedClass(2), UnorderedClass(2), generalized_value],
        ]
        k = 2
        k_anonymus_df, k_generalizations = Datafly(k, ['unordered'] * 4).depersonalize(df)
        self.assertEqual(df_expected, k_anonymus_df)
        self.assertEqual(k_generalizations, 2)

    def test_normal_1(self):
        df = [
            [1, 1, 1, 1],
            [1, 2, 1, 1],
            [2, 3, 2, 2],
            [2, 4, 2, 3],
        ]
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertEqual(k_changes, 6)

    def test_big_k(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
        ]
        k = 5
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertEqual(k_anonymus_df, None)
        self.assertEqual(k_changes, None)

    def test_generalize_everything(self):
        df = [
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [4, 4, 4, 4],
        ]
        k = 4
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        none_df = [[GeneralizationRange(1, 4, 'real', None)] * 4]*4
        self.assertEqual(k_anonymus_df, none_df)
        self.assertEqual(k_changes, 16)

    def test_k_equals_one(self):
        df = [
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [4, 4, 4, 4],
        ]
        k = 1
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertEqual(k_anonymus_df, df)
        self.assertEqual(k_changes, 0)

    def test_numpy(self):
        df = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [2, 2, 2, 2],
        ]
        df = np.array(df)
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertTrue((df == k_anonymus_df).all())
        self.assertEqual(k_changes, 0)

    def test_string_data(self):
        df = [
            ["a", "a", "a", "a"],
            ["a", "a", "a", "a"],
            ["b", "b", "b", "b"],
            ["b", "b", "b", "b"],
        ]
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['ordered']*4).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_changes, 0)

    def test_float_data(self):
        df = [
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [2.0, 2.0, 2.0, 2.0],
            [2.0, 2.0, 2.0, 2.0],
        ]
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['real']*4).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_changes, 0)

    def test_mixed_data(self):
        df = [
            [1.0, 1.0, "a", 1],
            [1.0, 1.0, "a", 1],
            [2.0, 2.0, "b", 2],
            [2.0, 2.0, "b", 2],
        ]
        k = 2
        k_anonymus_df, k_changes = Datafly(k, ['real', 'real', 'ordered', 'real']).depersonalize(df)
        self.assertEqual(df, k_anonymus_df)
        self.assertEqual(k_changes, 0)

    def test_random_df(self):
        seed = 1234
        random.seed(seed)
        np.random.seed(seed)
        for i in range(1000):
            rows = random.randint(4, 50)
            cols = random.randint(1, 5)
            df = np.random.randint(0, 3, (rows, cols))
            k = random.randint(2, 4)
            quasi_identifiers_types = []
            for j in range(cols):
                quasi_identifiers_types.append(random.choice(['real', 'ordered', 'unordered']))
            k_anonymus_df, k_changes = Datafly(k, quasi_identifiers_types).depersonalize(df)



if __name__ == '__main__':
    unittest.main()
