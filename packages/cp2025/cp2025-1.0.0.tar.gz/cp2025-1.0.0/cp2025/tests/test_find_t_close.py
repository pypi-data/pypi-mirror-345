import unittest
import numpy as np
from cp2025.utility.metrics import find_t_close
from cp2025.algorithms.SuppressionTClosenessBaseline import SuppressionTClosenessBaseline

class TestFindTClose(unittest.TestCase):

    def test_normal(self):
        df = np.array([
            [1, 1, 1, 1, 'a'],
            [1, 1, 1, 2, 'b'],
            [1, 1, 1, 3, 'c'],
            [1, 4, 4, 4, 'a'],
            [1, 4, 4, 5, 'b'],
        ])
        k = 2
        t = 0.075
        t_close_df, k_suppressions = SuppressionTClosenessBaseline(k, t, sensitives_types=['unordered']).depersonalize(
            df, sensitives_ids=[4])

        score = find_t_close(t_close_df[:,:4], t_close_df[:,4:5], ['unordered'])

        assert score <= t
        assert abs(score - t) < 0.005

if __name__ == '__main__':
    unittest.main()
