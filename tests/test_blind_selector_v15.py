import ast
import json
import tempfile
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_prefix_relations_v13_single_build)
from tools.blind_24_lattice_selector_v15 import (
    CONSTITUTIONAL_OBJECTIVES, generated_prefix_relations_v15,
    select_state_path_v15)
from tools.run_blind_protocol_v15 import run_protocol_v15
from verify.evaluate_sealed_blind_v15 import evaluate_v15


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV15Tests(unittest.TestCase):
    def test_spatial_relation_extends_only_hard_exclusion(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_prefix_relations_v13_single_build(sequence, path)
        v15 = generated_prefix_relations_v15(sequence, path)
        self.assertGreaterEqual(v15[0], v13[0])
        self.assertEqual(v15[1:], v13[1:])

    def test_selector_retains_fifteen_objectives_and_exposes_spatial_census(self):
        result = select_state_path_v15("MQIFVK")
        self.assertEqual(
            len(result["final_relations"]["objectives"]),
            CONSTITUTIONAL_OBJECTIVES)
        self.assertIn(
            "sidechain_spatial_exclusion", result["final_relations"])
        self.assertIn("sidechain_spatial_exclusion_census", result)

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v15.py").read_text().lower()
        tree = ast.parse(source)
        for prohibited in (
                "parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
            self.assertNotIn(prohibited, source)
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("calculate_tm", imported)

    def test_seal_boundary_precedes_target_comparison(self):
        manifest = ROOT / "verify/blind_selector_v15.json"
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v15-seal-boundary-test", "sequence": "MQ"}) + "\n")
            sealed = temporary / "sealed"
            seal = run_protocol_v15(manifest, selector_input, sealed)
            self.assertEqual(seal["status"], "completed")
            self.assertTrue((sealed / "prediction.pdb").is_file())
            result = evaluate_v15(
                manifest, sealed, sealed / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(result["tm_score"], 1.0)
            self.assertAlmostEqual(result["ca_drmsd_angstrom"], 0.0)


if __name__ == "__main__":
    unittest.main()
