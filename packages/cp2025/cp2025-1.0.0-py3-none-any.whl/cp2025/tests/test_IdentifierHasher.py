from numpy.ma.testutils import assert_equal
import unittest
import numpy as np
from cp2025.algorithms.IdentifierHasher import IdentifierHasher


class TestIdentifierHasher(unittest.TestCase):

    def test_normal(self):
        df = np.array([
            [1, 1.1, 1, 1, 'a'],
            [1, 1.2, 1, 2, 'b'],
            [1, 1.3, 1, 3, 'c'],
            [1, 4.4, 4, 4, 'a'],
            [1, 4.5, 4, 5, 'b'],
        ])
        correct_df = np.array([['3bf78480b96928bcf8dc715bf5a7c0fd1488ec85face703b02273e880f1d4513',
        '3bf78480b96928bcf8dc715bf5a7c0fd1488ec85face703b02273e880f1d4513',
        1, 1,
        '3bf78480b96928bcf8dc715bf5a7c0fd1488ec85face703b02273e880f1d4513'],
       ['04edd6195d331bb7e0407b5c9a4f1caec409ff1bafda0418ef37b8220b682520',
        '04edd6195d331bb7e0407b5c9a4f1caec409ff1bafda0418ef37b8220b682520',
        1, 2,
        '04edd6195d331bb7e0407b5c9a4f1caec409ff1bafda0418ef37b8220b682520'],
       ['951bf88ac22242a9371efa8c7e7640c77915cb0259abf225ff095704b5f6ca2e',
        '951bf88ac22242a9371efa8c7e7640c77915cb0259abf225ff095704b5f6ca2e',
        1, 3,
        '951bf88ac22242a9371efa8c7e7640c77915cb0259abf225ff095704b5f6ca2e'],
       ['4a2d2a1b9239aa17c495c663e918b81f68330b80c5a607d27b8c3e1c1610e8b5',
        '4a2d2a1b9239aa17c495c663e918b81f68330b80c5a607d27b8c3e1c1610e8b5',
         4, 4,
        '4a2d2a1b9239aa17c495c663e918b81f68330b80c5a607d27b8c3e1c1610e8b5'],
       ['d0b6aedf9722959109ea9316f5a95a301de14a756ce015a2d209660211104877',
        'd0b6aedf9722959109ea9316f5a95a301de14a756ce015a2d209660211104877',
        4, 5,
        'd0b6aedf9722959109ea9316f5a95a301de14a756ce015a2d209660211104877']])

        hashed_df = IdentifierHasher().depersonalize(df, identifiers_ids=[0, 1, 4], quasi_identifiers_ids=[2], sensitives_ids=[3])[0]

        assert_equal(correct_df, hashed_df)

if __name__ == '__main__':
    unittest.main()
