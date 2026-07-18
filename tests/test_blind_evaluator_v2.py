import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_protocol_v2 import run_protocol_v2
from verify.evaluate_sealed_blind_v2 import evaluate_v2


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verify/blind_selector_v2.json"


class BlindEvaluatorV2Tests(unittest.TestCase):
    def make_seal(self, root: Path) -> Path:
        selector_input = root / "input.json"
        selector_input.write_text(json.dumps(
            {"run_id": "synthetic-v2-eval", "sequence": "ACDEFGHI"},
            indent=2, sort_keys=True) + "\n")
        sealed = root / "sealed"
        run_protocol_v2(MANIFEST, selector_input, sealed)
        return sealed

    def test_tampered_prediction_fails_before_missing_target_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sealed = self.make_seal(root)
            with (sealed / "prediction.pdb").open("a") as handle:
                handle.write("REMARK tampered\n")
            with self.assertRaisesRegex(RuntimeError, "seal mismatch"):
                evaluate_v2(MANIFEST, sealed, root / "target-does-not-exist.pdb",
                            root / "evaluation.json")

    def test_synthetic_post_seal_comparison_succeeds(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sealed = self.make_seal(root)
            evidence = evaluate_v2(
                MANIFEST, sealed, sealed / "prediction.pdb", root / "evaluation.json")
            self.assertEqual(evidence["status"], "completed")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)
            self.assertAlmostEqual(evidence["ca_drmsd_angstrom"], 0.0)


if __name__ == "__main__":
    unittest.main()
