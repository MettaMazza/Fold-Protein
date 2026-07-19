import ast
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.blind_24_lattice_selector_v6 import (
    ALPHA_ANGLES_DEGREES, BETA_ANGLES_DEGREES, GENERATED_ORBIT_SIGNATURES,
    local_orientation_key, normalized_signed_quartet_volume,
    orientation_orbit_key, precursor_orbit_key, select_state_path_v6,
    verify_generated_orientation_modes)
from tools.run_blind_protocol_v6 import run_protocol_v6
from verify.evaluate_sealed_blind_v6 import evaluate_v6, verify_v6_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV6Tests(unittest.TestCase):
    def test_generated_modes_use_exact_forced_angle_fractions(self):
        self.assertEqual(
            tuple(str(value) for value in ALPHA_ANGLES_DEGREES),
            ("-60", "-45"))
        self.assertEqual(
            tuple(str(value) for value in BETA_ANGLES_DEGREES),
            ("-120", "135"))
        modes = verify_generated_orientation_modes()
        self.assertGreater(modes["alpha"], 0)
        self.assertLess(modes["beta"], 0)

    def test_signed_volume_distinguishes_reflection(self):
        coordinates = np.asarray([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
        ])
        reflected = coordinates.copy()
        reflected[:, 2] *= -1
        signed = normalized_signed_quartet_volume(coordinates)
        mirrored = normalized_signed_quartet_volume(reflected)
        self.assertAlmostEqual(signed, -mirrored, places=15)
        self.assertNotEqual(signed, mirrored)

    def test_precursor_keeps_exact_alpha_and_beta_preimages(self):
        alpha_psi = 9
        alpha_state = 8 * 24 + 9
        beta_psi = 21
        beta_state = 4 * 24 + 21
        self.assertEqual(precursor_orbit_key([alpha_psi, alpha_state]), (0,))
        self.assertEqual(precursor_orbit_key([beta_psi, beta_state]), (0,))

    def test_exact_generated_quartet_has_zero_orbit_distance(self):
        alpha_psi = 9
        alpha_state = 8 * 24 + 9
        path = [alpha_psi, alpha_state, alpha_state]
        self.assertAlmostEqual(
            orientation_orbit_key("AAAA", path)[0], 0.0, places=15)
        self.assertEqual(len(local_orientation_key("AAAA", path)), 4)

    def test_v6_import_closure_is_target_incapable(self):
        for relative in (
            "tools/blind_24_lattice_selector_v6.py",
            "tools/run_blind_protocol_v6.py",
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

    def test_v6_completes_real_sequence_and_records_orientation(self):
        result = select_state_path_v6("MQIF")
        self.assertEqual(len(result["states"]), 4)
        self.assertEqual(len(result["final_key"]), 7)
        self.assertEqual(len(result["orientation_trace"]), 1)
        self.assertIn(
            result["orientation_trace"][0]["nearest_generated_mode"],
            GENERATED_ORBIT_SIGNATURES)

    def test_protocol_seals_and_evaluator_opens_target_after_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v6-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v6.json"
            seal = run_protocol_v6(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v6")
            checked, states = verify_v6_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v6-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v6(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
