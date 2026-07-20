import ast
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_prefix_relations_v13_single_build)
from tools.blind_24_lattice_selector_v18 import (
    CONSTITUTIONAL_OBJECTIVES, HARD_EXCLUSION_STRATA,
    generated_prefix_relations_v18, select_state_path_v18)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV18Tests(unittest.TestCase):
    def test_graph_relation_preserves_backbone_hard_count_separately(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_prefix_relations_v13_single_build(sequence, path)
        v18 = generated_prefix_relations_v18(sequence, path)
        self.assertEqual(v18[0][0], v13[0])
        self.assertGreaterEqual(v18[0][1], 0)
        self.assertEqual(v18[1:], v13[1:])

    def test_selector_exposes_exact_hierarchy_and_v13_objectives(self):
        result = select_state_path_v18("MQIFVK")
        final = result["final_relations"]
        self.assertEqual(len(final["objectives"]), CONSTITUTIONAL_OBJECTIVES)
        self.assertEqual(final["hard_exclusion_strata"], list(HARD_EXCLUSION_STRATA))
        self.assertEqual(final["hard_exclusions"], sum(final["hard_exclusion_vector"]))

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v18.py").read_text().lower()
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
