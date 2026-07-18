import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_length_ladder_v2 import run_ladder, validate_registration
from tools.verify_blind_length_ladder_v2 import verify_ladder


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "verify/blind_selector_v2_length_ladder.json"


class BlindLengthLadderV2Tests(unittest.TestCase):
    def test_registration_is_sequence_only_and_hash_bound(self):
        registration, _ = validate_registration(REGISTRATION)
        self.assertEqual(registration["lengths"], [8, 16, 24, 32, 48, 76])
        self.assertNotIn("target", registration)
        self.assertNotIn("native", registration)

    def test_reordered_or_nonprefix_registration_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "registration.json"
            registration = json.loads(REGISTRATION.read_text())
            registration["lengths"] = [16, 8, 76]
            path.write_text(json.dumps(registration))
            with self.assertRaisesRegex(ValueError, "unique ascending"):
                validate_registration(path)

    def test_one_prefix_ladder_seals_verifies_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registration = json.loads(REGISTRATION.read_text())
            registration["sequence"] = registration["sequence"][:8]
            import hashlib
            registration["sequence_sha256"] = hashlib.sha256(
                registration["sequence"].encode()).hexdigest()
            registration["lengths"] = [8]
            path = root / "registration.json"
            path.write_text(json.dumps(registration, indent=2, sort_keys=True) + "\n")
            output = root / "sealed"
            seal = run_ladder(path, output)
            self.assertEqual(seal["status"], "completed")
            verification = verify_ladder(output)
            self.assertEqual(verification["completed_runs"], 1)
            self.assertEqual(verification["failed_runs"], 0)
            with self.assertRaises(FileExistsError):
                run_ladder(path, output)


if __name__ == "__main__":
    unittest.main()
