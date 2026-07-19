import ast
import json
import tempfile
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v14 import (
    CONSTITUTIONAL_OBJECTIVES, generated_prefix_relations_v14,
    select_state_path_v14)
from tools.run_blind_protocol_v14 import run_protocol_v14
from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_prefix_relations_v13_single_build)
from verify.evaluate_sealed_blind_v14 import evaluate_v14, verify_v14_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV14Tests(unittest.TestCase):
    def test_continuity_relations_extend_v13_once(self):
        sequence = "MQIFVKTL"
        path = [11, 201, 21, 309, 17, 205, 33]
        v13 = generated_prefix_relations_v13_single_build(sequence, path)
        v14 = generated_prefix_relations_v14(sequence, path)
        self.assertEqual(v14[:len(v13)], v13)
        self.assertEqual(len(v14), len(v13) + 2)
        self.assertTrue(all(isinstance(value, int) for value in v14[-2:]))

    def test_selector_exposes_seventeen_objectives_and_continuity(self):
        result = select_state_path_v14("MQIFVK")
        self.assertEqual(
            len(result["final_relations"]["objectives"]),
            CONSTITUTIONAL_OBJECTIVES)
        self.assertIn("hydrogen_bond_continuity", result["final_relations"])
        self.assertIn("hydrogen_bond_continuity_census", result)

    def test_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v14.py").read_text().lower()
        tree = ast.parse(source)
        for prohibited in (
                "parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
            self.assertNotIn(prohibited, source)
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("calculate_tm", imported)

    def test_v14_seals_before_target_evaluation(self):
        with tempfile.TemporaryDirectory() as held:
            root = Path(held)
            selector_input = root / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v14-test-mq", "sequence": "MQ"}))
            output = root / "sealed"
            manifest = ROOT / "verify/blind_selector_v14.json"
            seal = run_protocol_v14(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v14")
            checked, states = verify_v14_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v14-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v14(
                manifest, output, output / "prediction.pdb",
                root / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
