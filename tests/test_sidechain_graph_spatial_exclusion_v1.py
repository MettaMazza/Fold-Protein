import ast
import unittest
from pathlib import Path

import numpy as np

from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from tools.sidechain_graph_spatial_exclusion_v1 import (
    SIDECHAIN_COVALENT_BONDS, SIDECHAIN_GRAPH_SPATIAL_CENSUS,
    generated_sidechain_graph_points,
    sidechain_graph_spatial_exclusion_relation)


ROOT = Path(__file__).resolve().parents[1]


class SidechainGraphSpatialExclusionTests(unittest.TestCase):
    def _atoms(self, sequence):
        return build_backbone_coordinates(
            sequence, [-60.0] * len(sequence), [-45.0] * len(sequence))

    def test_all_twenty_covalent_graphs_close_without_empirical_geometry(self):
        census = SIDECHAIN_GRAPH_SPATIAL_CENSUS
        self.assertEqual(census["alphabet_count"], 20)
        self.assertEqual(set(SIDECHAIN_COVALENT_BONDS), set(census["alphabet"]))
        for field in (
                "empirical_bond_length", "empirical_bond_angle",
                "empirical_radius", "fitted_cutoff", "rotamer", "reward",
                "target"):
            self.assertIsNone(census[field])
        self.assertEqual(
            census["pair_exclusion_unit"],
            "1/2 fold of generated adjacent C-alpha step")

    def test_branch_atoms_receive_distinct_generated_points(self):
        points = generated_sidechain_graph_points("VV", self._atoms("VV"))[0]
        self.assertFalse(np.allclose(
            points["points"]["CG1"], points["points"]["CG2"]))

    def test_glycine_is_empty_and_graph_atom_count_is_exact(self):
        points = generated_sidechain_graph_points("GW", self._atoms("GW"))
        self.assertNotIn(0, points)
        self.assertEqual(points[1]["atom_count"], 10)

    def test_relation_is_scale_invariant(self):
        sequence = "VIVI"
        atoms = self._atoms(sequence)
        original = sidechain_graph_spatial_exclusion_relation(sequence, atoms)
        scaled = [dict(atom, coord=np.asarray(atom["coord"]) * 7) for atom in atoms]
        transformed = sidechain_graph_spatial_exclusion_relation(sequence, scaled)
        self.assertEqual(original["hard_exclusions"], transformed["hard_exclusions"])
        self.assertEqual(original["atom_encounter_count"], transformed["atom_encounter_count"])

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/sidechain_graph_spatial_exclusion_v1.py").read_text().lower()
        tree = ast.parse(source)
        for prohibited in (
                "parse_pdb", "target_pdb", "calculate_tm", "rotamer_geometry",
                "optimize_empirical"):
            self.assertNotIn(prohibited, source)
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("calculate_tm", imported)


if __name__ == "__main__":
    unittest.main()
