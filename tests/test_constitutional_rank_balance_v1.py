import unittest

from tools.constitutional_rank_balance_v1 import (
    select_balanced, symmetric_ordinal_vectors)


class ConstitutionalRankBalanceV1Tests(unittest.TestCase):
    def test_objective_permutation_does_not_change_vectors(self):
        rows = [
            (0, (1.0, 4.0, 2.0), (0,)),
            (0, (2.0, 1.0, 3.0), (1,)),
            (0, (3.0, 2.0, 1.0), (2,)),
        ]
        permuted = [
            (hard, (values[2], values[0], values[1]), identity)
            for hard, values, identity in rows
        ]
        self.assertEqual(
            symmetric_ordinal_vectors(rows),
            symmetric_ordinal_vectors(permuted))

    def test_strictly_increasing_reexpression_does_not_change_selection(self):
        rows = [
            (0, (1.0, 4.0), (0,)),
            (0, (2.0, 2.0), (1,)),
            (0, (4.0, 1.0), (2,)),
        ]
        transformed = [
            (hard, (left ** 3, 7 * right + 11), identity)
            for hard, (left, right), identity in rows
        ]
        self.assertEqual(
            [row[2] for row in select_balanced(rows, 2)],
            [row[2] for row in select_balanced(transformed, 2)])

    def test_hard_exclusion_is_absolute(self):
        rows = [
            (1, (0.0, 0.0), (0,)),
            (0, (100.0, 100.0), (1,)),
            (0, (200.0, 200.0), (2,)),
        ]
        self.assertEqual(
            [row[2] for row in select_balanced(rows, 2)], [(1,), (2,)])

    def test_boundary_ties_are_preserved_for_secondary_closure(self):
        rows = [
            (0, (0.0, 2.0), (0,)),
            (0, (2.0, 0.0), (1,)),
            (0, (1.0, 1.0), (2,)),
        ]
        selected = select_balanced(rows, 1, include_boundary_ties=True)
        self.assertGreaterEqual(len(selected), 1)
        boundary = symmetric_ordinal_vectors(rows)[selected[0][2]]
        self.assertTrue(all(
            symmetric_ordinal_vectors(rows)[row[2]] <= boundary
            for row in selected))


if __name__ == "__main__":
    unittest.main()
