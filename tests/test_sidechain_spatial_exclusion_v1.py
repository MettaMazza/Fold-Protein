import unittest

import numpy as np

from tools.blind_24_lattice_selector_v3 import build_lookahead_prefix
from tools.sidechain_spatial_exclusion_v1 import (
    SIDECHAIN_SPATIAL_EXCLUSION_CENSUS,
    generated_sidechain_command_points, sidechain_spatial_exclusion_relation,
    verify_sidechain_spatial_exclusion_constitution)


class SidechainSpatialExclusionTests(unittest.TestCase):
    def test_constitution_closes_without_empirical_geometry(self):
        census = verify_sidechain_spatial_exclusion_constitution()
        self.assertEqual(census, SIDECHAIN_SPATIAL_EXCLUSION_CENSUS)
        self.assertEqual(census["glycine_sidechain_atoms"], 0)
        self.assertIsNone(census["empirical_residue_radius"])
        self.assertIsNone(census["empirical_distance_cutoff"])
        self.assertIsNone(census["rotamer"])

    def test_glycine_has_no_spatial_command(self):
        atoms = build_lookahead_prefix("GG", [0])
        self.assertEqual(generated_sidechain_command_points("GG", atoms), {})
        self.assertEqual(
            sidechain_spatial_exclusion_relation("GG", atoms)[
                "hard_exclusions"], 0)

    def test_heavier_graph_has_larger_fold_share(self):
        atoms = build_lookahead_prefix("AW", [0])
        commands = generated_sidechain_command_points("AW", atoms)
        self.assertLess(commands[0]["reach_share"], commands[1]["reach_share"])
        self.assertEqual(commands[0]["reach_share"], 1 / 2)
        self.assertEqual(commands[1]["reach_share"], 10 / 11)

    def test_generated_command_uses_positive_l_chirality_half_space(self):
        atoms = build_lookahead_prefix("AA", [0])
        commands = generated_sidechain_command_points("AA", atoms)
        rows = [atoms[:3], atoms[3:6]]
        for index, row in enumerate(rows):
            by_name = {atom["name"]: np.asarray(atom["coord"]) for atom in row}
            normal = np.cross(
                by_name["N"] - by_name["CA"],
                by_name["C"] - by_name["CA"])
            self.assertGreater(float(np.dot(normal, commands[index]["direction"])), 0)

    def test_relation_is_scale_invariant(self):
        atoms = build_lookahead_prefix("AWAW", [0, 200, 309])
        original = sidechain_spatial_exclusion_relation("AWAW", atoms)
        scaled = [
            {**atom, "coord": np.asarray(atom["coord"]) * 7}
            for atom in atoms]
        transformed = sidechain_spatial_exclusion_relation("AWAW", scaled)
        self.assertEqual(
            original["hard_exclusions"], transformed["hard_exclusions"])
        self.assertEqual(
            original["excluded_residue_pair_count"],
            transformed["excluded_residue_pair_count"])


if __name__ == "__main__":
    unittest.main()
