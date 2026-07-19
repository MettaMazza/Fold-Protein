import unittest

import numpy as np

from tools.residue_steric_constitution_v1 import (
    SIDECHAIN_HEAVY_ATOM_COUNT,
    dimensionless_sidechain_crowding_relation,
    verify_steric_constitution,
)


class ResidueStericConstitutionV1Tests(unittest.TestCase):
    def test_graphs_are_exhaustive_and_exact_at_census_boundaries(self):
        census = verify_steric_constitution()
        self.assertEqual(census["alphabet_count"], 20)
        self.assertEqual(SIDECHAIN_HEAVY_ATOM_COUNT["G"], 0)
        self.assertEqual(SIDECHAIN_HEAVY_ATOM_COUNT["A"], 1)
        self.assertEqual(SIDECHAIN_HEAVY_ATOM_COUNT["W"], 10)
        self.assertEqual(census["sidechain_heavy_atoms"]["D"],
                         ["CB", "CG", "OD1", "OD2"])

    def test_more_counted_encounters_mean_more_crowding(self):
        coordinates = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
        ])
        glycine = dimensionless_sidechain_crowding_relation(
            "GAG", coordinates)
        alanine = dimensionless_sidechain_crowding_relation(
            "AAA", coordinates)
        tryptophan = dimensionless_sidechain_crowding_relation(
            "WAW", coordinates)
        self.assertEqual(glycine, 0.0)
        self.assertLess(glycine, alanine)
        self.assertLess(alanine, tryptophan)

    def test_greater_generated_separation_means_less_crowding(self):
        near = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ])
        far = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [3.0, 0.0, 0.0],
        ])
        self.assertLess(
            dimensionless_sidechain_crowding_relation("WGGW", far),
            dimensionless_sidechain_crowding_relation("WGGW", near))

    def test_relation_is_dimensionless_under_uniform_scaling(self):
        coordinates = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [3.0, 1.0, 1.0],
        ])
        original = dimensionless_sidechain_crowding_relation(
            "FAWY", coordinates)
        scaled = dimensionless_sidechain_crowding_relation(
            "FAWY", coordinates * 11)
        self.assertAlmostEqual(original, scaled, places=13)


if __name__ == "__main__":
    unittest.main()
