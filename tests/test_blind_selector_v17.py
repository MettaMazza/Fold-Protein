import ast
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_prefix_relations_v13_single_build)
from tools.blind_24_lattice_selector_v17 import (
    CONSTITUTIONAL_OBJECTIVES, generated_prefix_relations_v17,
    select_state_path_v17)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV17Tests(unittest.TestCase):
    def test_graph_spatial_relation_extends_only_hard_exclusion(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_prefix_relations_v13_single_build(sequence, path)
        v17 = generated_prefix_relations_v17(sequence, path)
        self.assertGreaterEqual(v17[0], v13[0])
        self.assertEqual(v17[1:], v13[1:])

    def test_selector_retains_v13_objectives_and_exposes_graph_census(self):
        result = select_state_path_v17("MQIFVK")
        self.assertEqual(
            len(result["final_relations"]["objectives"]),
            CONSTITUTIONAL_OBJECTIVES)
        spatial = result["final_relations"]["sidechain_graph_spatial_exclusion"]
        self.assertEqual(
            spatial["hard_exclusions"], spatial["excluded_residue_pair_count"])
        self.assertIn("sidechain_graph_spatial_census", result)

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v17.py").read_text().lower()
        tree = ast.parse(source)
        for prohibited in (
                "parse_pdb", "target_pdb", "optimize_empirical", "compute_tm",
                "rotamer_geometry"):
            self.assertNotIn(prohibited, source)
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("calculate_tm", imported)


if __name__ == "__main__":
    unittest.main()
