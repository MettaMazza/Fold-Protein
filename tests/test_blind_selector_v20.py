import ast
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13 import generated_local_relations_v13
from tools.blind_24_lattice_selector_v20 import (
    generated_local_relations_v20, generated_prefix_relations_v20,
    select_state_path_v20)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV20Tests(unittest.TestCase):
    def test_local_relations_are_exact_v13_with_empty_graph_children(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_local_relations_v13(sequence, path)
        v20 = generated_local_relations_v20(sequence, path)
        self.assertEqual(v20[0], v13[0])
        self.assertEqual(v20[1], (v13[1], 0, 0))
        self.assertEqual(v20[2:], v13[2:])

    def test_complete_prefix_contains_exact_graph_child_counts(self):
        relation = generated_prefix_relations_v20(
            "MQIFVKTL", [11, 201, 21, 309, 17, 205, 33])
        self.assertEqual(len(relation[0]), 3)
        self.assertGreaterEqual(relation[0][1], 0)
        self.assertGreaterEqual(relation[0][2], relation[0][1])

    def test_selector_declares_three_level_global_hierarchy(self):
        result = select_state_path_v20("MQIFVK")
        self.assertFalse(result["local_graph_pruning"])
        self.assertEqual(
            result["final_relations"]["hard_exclusion_strata"],
            ["backbone", "sidechain_graph_pair",
             "sidechain_graph_atom_encounter"])

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v20.py").read_text().lower()
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
