import ast
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_prefix_relations_v13_single_build)
from tools.blind_24_lattice_selector_v15 import generated_prefix_relations_v15
from tools.blind_24_lattice_selector_v16 import (
    CONSTITUTIONAL_OBJECTIVES, generated_prefix_relations_v16,
    select_state_path_v16)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV16Tests(unittest.TestCase):
    def test_binary_spatial_relation_extends_only_hard_exclusion(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_prefix_relations_v13_single_build(sequence, path)
        v15 = generated_prefix_relations_v15(sequence, path)
        v16 = generated_prefix_relations_v16(sequence, path)
        self.assertGreaterEqual(v16[0], v13[0])
        self.assertLessEqual(v16[0], v15[0])
        self.assertEqual(v16[1:], v13[1:])

    def test_selector_retains_fifteen_objectives_and_binary_spatial_census(self):
        result = select_state_path_v16("MQIFVK")
        self.assertEqual(
            len(result["final_relations"]["objectives"]),
            CONSTITUTIONAL_OBJECTIVES)
        spatial = result["final_relations"]["sidechain_spatial_exclusion"]
        self.assertEqual(
            spatial["hard_exclusions"],
            spatial["excluded_residue_pair_count"])
        self.assertIn("sidechain_spatial_exclusion_census", result)

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v16.py").read_text().lower()
        tree = ast.parse(source)
        for prohibited in (
                "parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
            self.assertNotIn(prohibited, source)
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("calculate_tm", imported)


if __name__ == "__main__":
    unittest.main()
