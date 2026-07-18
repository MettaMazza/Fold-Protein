import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.blind_24_lattice_solver import (
    CANONICAL_STATE,
    SFT_CANDIDATES,
    SelectorConfig,
    active_candidates,
    build_lookahead_prefix,
    select_state_path,
)
from tools.run_blind_protocol import run_protocol
from verify.evaluate_sealed_blind import evaluate, verify_seal


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verify/blind_selector_v1.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BlindProtocolTests(unittest.TestCase):
    def test_lattice_and_boundary_mapping(self):
        self.assertEqual(len(SFT_CANDIDATES), 576)
        self.assertEqual(list(active_candidates(0, 3)), list(range(24)))
        self.assertEqual(len(list(active_candidates(1, 3))), 576)
        self.assertEqual(tuple(active_candidates(2, 3)), ())

    def test_one_residue_lookahead_is_causal(self):
        first = build_lookahead_prefix("AC", [0])
        second = build_lookahead_prefix("AC", [1])
        ca_first = np.asarray([a["coord"] for a in first if a["name"] == "CA"])
        ca_second = np.asarray([a["coord"] for a in second if a["name"] == "CA"])
        self.assertFalse(np.allclose(ca_first[-1], ca_second[-1]))

    def test_selector_is_deterministic_and_canonicalizes_final_state(self):
        config = SelectorConfig(beam_width=2)
        first = select_state_path("ACD", config)
        second = select_state_path("ACD", config)
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["score_trace"], second["score_trace"])
        self.assertEqual(first["states"][-1], CANONICAL_STATE)

    def _small_manifest(self, directory):
        data = json.loads(MANIFEST.read_text())
        data["selector_config"]["beam_width"] = 2
        path = directory / "manifest.json"
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        return path

    def test_input_rejects_target_capability(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            manifest = self._small_manifest(temp)
            bad_input = temp / "input.json"
            bad_input.write_text(json.dumps({"run_id": "x", "sequence": "ACD",
                                             "target": "native.pdb"}))
            with self.assertRaisesRegex(ValueError, "only run_id and sequence"):
                run_protocol(manifest, bad_input, temp / "sealed")

    def test_deterministic_seal_and_target_isolation(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            manifest = self._small_manifest(temp)
            selector_input = temp / "input.json"
            selector_input.write_text('{"run_id":"protocol-test","sequence":"ACD"}\n')
            first_dir = temp / "first"
            second_dir = temp / "second"
            first = run_protocol(manifest, selector_input, first_dir)
            second = run_protocol(manifest, selector_input, second_dir)
            self.assertEqual(first, second)
            self.assertEqual((first_dir / "prediction.pdb").read_bytes(),
                             (second_dir / "prediction.pdb").read_bytes())

            (first_dir / "prediction.pdb").write_text("tampered\n")
            with self.assertRaisesRegex(RuntimeError, "seal mismatch"):
                verify_seal(manifest, first_dir)
            with self.assertRaisesRegex(RuntimeError, "seal mismatch"):
                evaluate(manifest, first_dir, temp / "target-does-not-exist.pdb",
                         temp / "evaluation.json")

            evidence = evaluate(manifest, second_dir, ROOT / "verify/1ubq.pdb",
                                temp / "valid-evaluation.json")
            self.assertEqual(evidence["status"], "completed")
            self.assertEqual(evidence["matched_ca_atoms"], 3)

    def test_protected_construction_hashes(self):
        manifest = json.loads(MANIFEST.read_text())
        for relative, expected in manifest["protected_construction_sha256"].items():
            self.assertEqual(sha256(ROOT / relative), expected, relative)


if __name__ == "__main__":
    unittest.main()
