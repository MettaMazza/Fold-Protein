import ast
from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v7 import (
    BINARY_MODE_COUNT, MODE_CAPACITY, MODE_NAMES, candidate_mode,
    forced_mode_capacity, select_state_path_v7)
from tools.run_blind_protocol_v7 import run_protocol_v7
from verify.evaluate_sealed_blind_v7 import evaluate_v7, verify_v7_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV7Tests(unittest.TestCase):
    def test_binary_count_divides_24_frontier_exactly(self):
        self.assertEqual(BINARY_MODE_COUNT, 2)
        self.assertEqual(MODE_CAPACITY, 12)
        self.assertEqual(forced_mode_capacity(), 12)
        self.assertEqual(BINARY_MODE_COUNT * MODE_CAPACITY, 24)

    def test_initial_axis_census_is_twelve_per_mode(self):
        census = Counter(candidate_mode("MQ", [state]) for state in range(24))
        self.assertEqual(census, Counter({"alpha": 12, "beta": 12}))

    def test_both_modes_survive_each_complete_frontier(self):
        result = select_state_path_v7("MQIF")
        self.assertEqual(len(result["mode_balance_trace"]), 3)
        for row in result["mode_balance_trace"]:
            self.assertEqual(set(row), set(MODE_NAMES))
            for mode in MODE_NAMES:
                self.assertGreater(row[mode]["retained"], 0)
        for row in result["mode_balance_trace"][1:]:
            self.assertEqual(row["alpha"]["retained"], MODE_CAPACITY)
            self.assertEqual(row["beta"]["retained"], MODE_CAPACITY)

    def test_v7_import_closure_is_target_incapable(self):
        for relative in (
            "tools/blind_24_lattice_selector_v7.py",
            "tools/run_blind_protocol_v7.py",
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

    def test_v7_completes_real_sequence_and_records_balance(self):
        result = select_state_path_v7("MQIF")
        self.assertEqual(len(result["states"]), 4)
        self.assertEqual(len(result["final_key"]), 7)
        self.assertEqual(len(result["orientation_trace"]), 1)
        self.assertEqual(result["mode_capacity"], 12)

    def test_protocol_seals_and_evaluator_opens_target_after_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v7-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v7.json"
            seal = run_protocol_v7(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v7")
            checked, states = verify_v7_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v7-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v7(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
