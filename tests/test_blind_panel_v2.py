import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_panel_v2 import run_panel
from tools.verify_blind_panel_v2 import verify_panel


ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "verify/blind_selector_v2_panel.json"


class BlindPanelV2Tests(unittest.TestCase):
    def test_panel_contains_no_target_capability(self):
        panel = json.loads(PANEL.read_text())
        self.assertEqual(len(panel["sequences"]), 5)
        for row in panel["sequences"]:
            self.assertEqual(set(row), {"run_id", "sequence", "diagnostic_role"})

    def test_small_registered_panel_seals_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            panel = json.loads(PANEL.read_text())
            panel["sequences"] = panel["sequences"][:1]
            panel_path = temp / "panel.json"
            panel_path.write_text(json.dumps(panel, indent=2, sort_keys=True) + "\n")
            output = temp / "sealed"
            seal = run_panel(panel_path, output)
            self.assertEqual(seal["status"], "completed")
            self.assertEqual(
                seal["execution"],
                "five-sequence selector-v2 panel")
            self.assertEqual(verify_panel(output)["verified_runs"], 1)
            with self.assertRaises(FileExistsError):
                run_panel(panel_path, output)


if __name__ == "__main__":
    unittest.main()
