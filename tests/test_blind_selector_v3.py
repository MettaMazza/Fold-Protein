import ast
import json
import math
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v2 import select_state_path_v2
from tools.blind_24_lattice_selector_v3 import select_state_path_v3
from tools.run_blind_protocol_v3 import run_protocol_v3


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV3Tests(unittest.TestCase):
    def test_v3_rederives_v2_path_without_legacy_runtime_imports(self):
        for sequence in ("MQ", "MQIF", "VILM"):
            v2 = select_state_path_v2(sequence)
            v3 = select_state_path_v3(sequence)
            self.assertEqual(v3["states"], v2["states"])
            self.assertEqual(v3["score_trace"], v2["score_trace"])
            self.assertEqual(v3["final_key"], v2["final_key"])
            self.assertEqual(v3["atoms"], v2["atoms"])

    def test_v3_import_closure_is_target_incapable(self):
        allowed_project_modules = {
            "tools.protein_backbone_geometry_v1",
            "protein_backbone_geometry_v1",
        }
        for relative in (
            "tools/blind_24_lattice_selector_v3.py",
            "tools/protein_backbone_geometry_v1.py",
        ):
            tree = ast.parse((ROOT / relative).read_text())
            imported = {
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            }
            project_imports = {
                name for name in imported
                if name.startswith("tools.") or name == "protein_backbone_geometry_v1"
            }
            self.assertTrue(project_imports <= allowed_project_modules)
            text = (ROOT / relative).read_text().lower()
            for prohibited in ("parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
                self.assertNotIn(prohibited, text)

    def test_lattice_has_exact_declared_census(self):
        from tools.blind_24_lattice_selector_v3 import LATTICE_DEGREES, LATTICE_STATES
        self.assertEqual(len(LATTICE_DEGREES), 24)
        self.assertEqual(len(LATTICE_STATES), 576)
        self.assertEqual(LATTICE_DEGREES[0], -180)
        self.assertEqual(LATTICE_DEGREES[-1], 165)

    def test_v3_protocol_seals_immutable_target_free_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v3-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            seal = run_protocol_v3(
                ROOT / "verify/blind_selector_v3.json", selector_input, output
            )
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v3")
            self.assertEqual(seal["status"], "completed")
            self.assertEqual(seal["path_length"], 2)
            self.assertTrue((output / "prediction.pdb").is_file())
            with self.assertRaises(FileExistsError):
                run_protocol_v3(
                    ROOT / "verify/blind_selector_v3.json", selector_input, output
                )


if __name__ == "__main__":
    unittest.main()
