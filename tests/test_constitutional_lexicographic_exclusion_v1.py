import unittest

from tools.constitutional_lexicographic_exclusion_v1 import (
    select_balanced_hierarchy)


class ConstitutionalLexicographicExclusionTests(unittest.TestCase):
    def test_parent_backbone_exclusion_precedes_child_sidechain_count(self):
        rows = [
            ((0, 9), (0.0,), (0,)),
            ((1, 0), (0.0,), (1,)),
        ]
        self.assertEqual(
            select_balanced_hierarchy(rows, 1)[0][2], (0,))

    def test_sidechain_exclusion_breaks_equal_backbone_stratum(self):
        rows = [
            ((2, 1), (9.0,), (0,)),
            ((2, 0), (99.0,), (1,)),
        ]
        self.assertEqual(
            select_balanced_hierarchy(rows, 1)[0][2], (1,))

    def test_soft_balance_acts_only_inside_identical_hard_vector(self):
        rows = [
            ((0, 0), (0.0, 0.0), (0,)),
            ((0, 0), (1.0, 1.0), (1,)),
        ]
        self.assertEqual(
            select_balanced_hierarchy(rows, 1)[0][2], (0,))


if __name__ == "__main__":
    unittest.main()
