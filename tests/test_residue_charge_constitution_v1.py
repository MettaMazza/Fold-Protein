import unittest

import numpy as np

from tools.residue_charge_constitution_v1 import (
    CHARGE_SIGN, dimensionless_electrostatic_relation,
    verify_charge_constitution)


class ResidueChargeConstitutionV1Tests(unittest.TestCase):
    def test_charge_classes_are_exhaustive_disjoint_and_exact(self):
        census = verify_charge_constitution()
        self.assertEqual(census["alphabet_count"], 20)
        self.assertEqual(census["classes"]["positive"], "KR")
        self.assertEqual(census["classes"]["negative"], "DE")
        self.assertEqual(CHARGE_SIGN["K"], 1)
        self.assertEqual(CHARGE_SIGN["D"], -1)
        self.assertEqual(CHARGE_SIGN["H"], 0)

    def test_opposite_and_like_sign_relations_order_without_weight(self):
        coordinates = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
        ])
        opposite = dimensionless_electrostatic_relation("KAD", coordinates)
        like = dimensionless_electrostatic_relation("KAR", coordinates)
        neutral = dimensionless_electrostatic_relation("AAA", coordinates)
        self.assertLess(opposite, neutral)
        self.assertLess(neutral, like)

    def test_relation_is_dimensionless_under_uniform_scaling(self):
        coordinates = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [3.0, 1.0, 1.0],
        ])
        original = dimensionless_electrostatic_relation("KADR", coordinates)
        scaled = dimensionless_electrostatic_relation(
            "KADR", coordinates * 7)
        self.assertAlmostEqual(original, scaled, places=15)


if __name__ == "__main__":
    unittest.main()
