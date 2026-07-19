import ast
import json
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v7 import select_state_path_v7
from tools.blind_24_lattice_selector_v8 import (
    generated_local_relations, generated_prefix_relations,
    select_state_path_v8)
from tools.run_blind_protocol_v8 import run_protocol_v8
from verify.evaluate_sealed_blind_v8 import evaluate_v8, verify_v8_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV8Tests(unittest.TestCase):
    def test_neutral_sequence_preserves_v7_path(self):
        v7 = select_state_path_v7("AAAA")
        v8 = select_state_path_v8("AAAA")
        self.assertEqual(v8["states"], v7["states"])

    def test_charged_sequence_changes_generated_relation(self):
        neutral = generated_prefix_relations("AAAA", [9, 200, 309])
        charged = generated_prefix_relations("KADK", [9, 200, 309])
        self.assertEqual(neutral[1], 0.0)
        self.assertNotEqual(charged[1], 0.0)
        self.assertEqual(len(generated_local_relations(
            "KADK", [9, 200, 309])), 5)

    def test_v8_retains_binary_mode_capacity(self):
        result = select_state_path_v8("KADK")
        self.assertEqual(result["mode_capacity"], 12)
        self.assertEqual(len(result["final_key"]), 9)
        for row in result["mode_balance_trace"][1:]:
            self.assertEqual(row["alpha"]["retained"], 12)
            self.assertEqual(row["beta"]["retained"], 12)

    def test_v8_import_closure_is_target_incapable(self):
        for relative in (
            "tools/blind_24_lattice_selector_v8.py",
            "tools/run_blind_protocol_v8.py",
            "tools/residue_charge_constitution_v1.py",
        ):
            tree = ast.parse((ROOT / relative).read_text())
            source = (ROOT / relative).read_text().lower()
            for prohibited in (
                    "parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
                self.assertNotIn(prohibited, source)
            imported = {
                node.module for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module}
            self.assertNotIn("calculate_tm", imported)

    def test_protocol_seals_and_evaluator_opens_target_after_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v8-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v8.json"
            seal = run_protocol_v8(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v8")
            checked, states = verify_v8_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v8-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v8(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
