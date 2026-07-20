import ast
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13 import generated_local_relations_v13
from tools.blind_24_lattice_selector_v19 import (
    generated_local_relations_v19, generated_prefix_relations_v19,
    select_state_path_v19)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV19Tests(unittest.TestCase):
    def test_local_relations_are_exact_v13_with_empty_child_hard_stratum(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_local_relations_v13(sequence, path)
        v19 = generated_local_relations_v19(sequence, path)
        self.assertEqual(v19[0], v13[0])
        self.assertEqual(v19[1], (v13[1], 0))
        self.assertEqual(v19[2:], v13[2:])

    def test_complete_prefix_contains_graph_child_stratum(self):
        relation = generated_prefix_relations_v19(
            "MQIFVKTL", [11, 201, 21, 309, 17, 205, 33])
        self.assertEqual(len(relation[0]), 2)
        self.assertGreaterEqual(relation[0][1], 0)

    def test_selector_declares_global_only_graph_route(self):
        result = select_state_path_v19("MQIFVK")
        self.assertFalse(result["local_graph_pruning"])
        self.assertEqual(
            result["final_relations"]["hard_exclusion_strata"],
            ["backbone", "sidechain_graph"])

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v19.py").read_text().lower()
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
