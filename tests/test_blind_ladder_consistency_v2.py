import unittest

from tools.analyze_blind_ladder_consistency_v2 import continuation_rows


class BlindLadderConsistencyV2Tests(unittest.TestCase):
    def test_final_canonical_state_is_not_compared_as_an_active_decision(self):
        rows = continuation_rows([
            (4, [10, 11, 12, 0]),
            (6, [10, 11, 99, 13, 14, 0]),
        ])
        self.assertEqual(rows, [{
            "short_length": 4,
            "long_length": 6,
            "active_states_compared": 3,
            "identical_active_states": 2,
            "first_divergence_zero_based": 2,
        }])

    def test_path_length_mismatch_halts(self):
        with self.assertRaisesRegex(ValueError, "path length"):
            continuation_rows([(3, [1, 0]), (4, [1, 2, 3, 0])])


if __name__ == "__main__":
    unittest.main()
