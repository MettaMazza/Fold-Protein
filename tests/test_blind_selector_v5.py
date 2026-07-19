import ast
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.blind_24_lattice_selector_v3 import build_lookahead_prefix
from tools.blind_24_lattice_selector_v5 import (
    BINARY_PLANE_OVERLAP, COLOUR_PLANE_WINDOW, ORIENTATION_QUARTET,
    complete_prefix_key, interwindow_orientation_key, locally_eligible,
    select_state_path_v5, verify_orientation_constitution)
from tools.run_blind_protocol_v5 import run_protocol_v5
from verify.evaluate_sealed_blind_v5 import evaluate_v5, verify_v5_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV5Tests(unittest.TestCase):
    def test_two_colour_planes_form_orientation_quartet(self):
        relation = verify_orientation_constitution()
        self.assertEqual(COLOUR_PLANE_WINDOW, 3)
        self.assertEqual(BINARY_PLANE_OVERLAP, 2)
        self.assertEqual(ORIENTATION_QUARTET, 4)
        self.assertEqual(relation["overlap_residues"], 3)
        self.assertEqual(relation["new_residues_per_step"], 1)

    def test_local_key_is_terminal_quartet_of_complete_prefix(self):
        sequence = "MQIFV"
        state_path = [2, 137, 401, 288]
        atoms = build_lookahead_prefix(sequence, state_path)
        ca = np.asarray([
            atom["coord"] for atom in atoms if atom["name"] == "CA"],
            dtype=float)
        from tools.blind_24_lattice_selector_v3 import dimensionless_topology_key
        expected = dimensionless_topology_key(sequence[-4:], ca[-4:])
        observed = interwindow_orientation_key(sequence, state_path)
        for actual, held in zip(observed, expected):
            self.assertAlmostEqual(actual, held, places=12)

    def test_local_frontier_preserves_every_boundary_tie(self):
        candidates = [
            ((0, 1.0, 0.0), (0,)),
            ((0, 1.0, 1.0), (1,)),
            ((0, 1.0, 1.0), (2,)),
            ((0, 1.0, 2.0), (3,)),
        ]
        held = locally_eligible(candidates, 2)
        self.assertEqual([path for _, path in held], [(0,), (1,), (2,)])

    def test_v5_import_closure_is_target_incapable(self):
        for relative in (
            "tools/blind_24_lattice_selector_v5.py",
            "tools/run_blind_protocol_v5.py",
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

    def test_v5_completes_a_real_sequence_prefix(self):
        result = select_state_path_v5("MQIF")
        self.assertEqual(len(result["states"]), 4)
        self.assertEqual(len(result["final_key"]), 6)
        self.assertEqual(len(result["score_trace"]), 3)
        self.assertEqual(len([
            atom for atom in result["atoms"] if atom["name"] == "CA"]), 4)

    def test_protocol_seals_and_evaluator_opens_target_after_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v5-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v5.json"
            seal = run_protocol_v5(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v5")
            checked, states = verify_v5_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v5-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v5(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
