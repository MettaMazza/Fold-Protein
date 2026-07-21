import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_panel_v35 import run_panel
from tools.verify_blind_panel_v35 import verify_panel


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "verify/blind_selector_v35_paired_panel.json"


class BlindPanelV35Tests(unittest.TestCase):
    def test_registration_is_multi_protein_and_target_incapable(self):
        registration = json.loads(REGISTRATION.read_text())
        self.assertEqual(len(registration["proteins"]), 2)
        self.assertEqual(list(registration["selectors"]), ["v34", "v35"])
        self.assertNotIn("target", REGISTRATION.read_text().lower())

    def test_small_paired_panel_seals_verifies_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registration = json.loads(REGISTRATION.read_text())
            registration["panel_id"] = "v35-unit-paired-panel"
            registration["proteins"] = [
                {"protein_id": "first", "sequence": "MQIFVKTL"},
                {"protein_id": "second", "sequence": "MEQRITLK"},
            ]
            registration_path = root / "registration.json"
            registration_path.write_text(
                json.dumps(registration, indent=2, sort_keys=True) + "\n")
            output = root / "sealed"
            seal = run_panel(registration_path, output)
            self.assertEqual(seal["prediction_count"], 4)
            self.assertEqual(verify_panel(output)["verified_predictions"], 4)
            with self.assertRaises(FileExistsError):
                run_panel(registration_path, output)


if __name__ == "__main__":
    unittest.main()
