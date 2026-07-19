import ast
import json
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v8 import select_state_path_v8
from tools.blind_24_lattice_selector_v9 import (
    generated_local_relations, generated_prefix_relations,
    select_state_path_v9)
from tools.run_blind_protocol_v9 import run_protocol_v9
from verify.evaluate_sealed_blind_v9 import evaluate_v9, verify_v9_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV9Tests(unittest.TestCase):
    def test_glycine_only_sequence_preserves_v8_path(self):
        v8 = select_state_path_v8("GGGG")
        v9 = select_state_path_v9("GGGG")
        self.assertEqual(v9["states"], v8["states"])

    def test_sidechain_graph_changes_generated_relation(self):
        glycine = generated_prefix_relations("GGGG", [9, 200, 309])
        bulky = generated_prefix_relations("WGGW", [9, 200, 309])
        self.assertEqual(glycine[1], 0.0)
        self.assertGreater(bulky[1], 0.0)
        self.assertEqual(len(generated_local_relations(
            "WGGW", [9, 200, 309])), 6)

    def test_v9_retains_binary_mode_capacity(self):
        result = select_state_path_v9("WGGW")
        self.assertEqual(result["mode_capacity"], 12)
        self.assertEqual(len(result["final_key"]), 11)
        for row in result["mode_balance_trace"][1:]:
            self.assertEqual(row["alpha"]["retained"], 12)
            self.assertEqual(row["beta"]["retained"], 12)

    def test_v9_import_closure_is_target_incapable(self):
        for relative in (
            "tools/blind_24_lattice_selector_v9.py",
            "tools/run_blind_protocol_v9.py",
            "tools/residue_steric_constitution_v1.py",
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
                "run_id": "v9-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v9.json"
            seal = run_protocol_v9(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v9")
            checked, states = verify_v9_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v9-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v9(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
