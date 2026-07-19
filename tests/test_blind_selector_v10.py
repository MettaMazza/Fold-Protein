import ast
import json
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v10 import select_state_path_v10
from tools.run_blind_protocol_v10 import run_protocol_v10
from verify.evaluate_sealed_blind_v10 import evaluate_v10, verify_v10_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV10Tests(unittest.TestCase):
    def test_v10_retains_binary_mode_capacity(self):
        result = select_state_path_v10("WGGW")
        self.assertEqual(result["mode_capacity"], 12)
        self.assertEqual(len(result["final_relations"]["objectives"]), 9)
        self.assertEqual(
            len(result["final_relations"]["ordinal_rank_vector"]), 9)
        for row in result["mode_balance_trace"][1:]:
            self.assertEqual(row["alpha"]["retained"], 12)
            self.assertEqual(row["beta"]["retained"], 12)

    def test_v10_is_deterministic(self):
        first = select_state_path_v10("KADKW")
        second = select_state_path_v10("KADKW")
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["final_relations"], second["final_relations"])

    def test_v10_import_closure_is_target_incapable(self):
        for relative in (
            "tools/blind_24_lattice_selector_v10.py",
            "tools/constitutional_rank_balance_v1.py",
            "tools/run_blind_protocol_v10.py",
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
                "run_id": "v10-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v10.json"
            seal = run_protocol_v10(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v10")
            checked, states = verify_v10_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v10-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v10(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
