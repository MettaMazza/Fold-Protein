import ast
import json
import math
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v2 import select_state_path_v2
from tools.blind_24_lattice_selector_v3 import select_state_path_v3
from tools.run_blind_protocol_v3 import run_protocol_v3
from verify.evaluate_sealed_blind_v3 import evaluate_v3, verify_v3_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV3Tests(unittest.TestCase):
    def test_v3_recomputes_v2_path_without_legacy_runtime_imports(self):
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
            "tools.residue_partition_v1",
            "residue_partition_v1",
        }
        for relative in (
            "tools/blind_24_lattice_selector_v3.py",
            "tools/protein_backbone_geometry_v1.py",
            "tools/residue_partition_v1.py",
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
        from tools.blind_24_lattice_selector_v3 import (
            LATTICE_DEGREES, LATTICE_STATES, forced_beam_width)
        self.assertEqual(len(LATTICE_DEGREES), 24)
        self.assertEqual(len(LATTICE_STATES), 576)
        self.assertEqual(LATTICE_DEGREES[0], -180)
        self.assertEqual(LATTICE_DEGREES[-1], 165)
        self.assertEqual(forced_beam_width(), 24)

    def test_registered_residue_partition_is_exhaustive_and_disjoint(self):
        from tools.residue_partition_v1 import (
            AMINO_ACIDS, HYDROPHOBIC_PACKING, REGISTERED_PARTITION,
            verify_registered_partition)
        census = verify_registered_partition()
        self.assertEqual(census["alphabet_count"], 20)
        self.assertEqual(set().union(*REGISTERED_PARTITION.values()), AMINO_ACIDS)
        classes = list(REGISTERED_PARTITION.values())
        self.assertFalse(classes[0] & classes[1])
        self.assertEqual(HYDROPHOBIC_PACKING, frozenset("VILMFWCY"))

    def test_protocol_rejects_a_caller_selected_beam_width(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            manifest = json.loads((ROOT / "verify/blind_selector_v3.json").read_text())
            manifest["selector_config"]["beam_width"] = 23
            manifest_path = temporary / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v3-reject-beam", "sequence": "MQ",
            }))
            with self.assertRaisesRegex(RuntimeError, "forced lattice-axis census"):
                run_protocol_v3(manifest_path, selector_input, temporary / "sealed")

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

    def test_v3_post_seal_evaluation_rejects_tampering_before_target_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v3-tamper-test", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            run_protocol_v3(
                ROOT / "verify/blind_selector_v3.json", selector_input, output
            )
            states = json.loads((output / "selected_states.json").read_text())
            states["states"][0] = 23
            (output / "selected_states.json").write_text(json.dumps(states))
            missing_target = temporary / "target-must-not-be-opened.pdb"
            with self.assertRaisesRegex(RuntimeError, "seal mismatch"):
                evaluate_v3(
                    ROOT / "verify/blind_selector_v3.json", output,
                    missing_target, temporary / "evaluation.json"
                )

    def test_v3_post_seal_evaluation_accepts_complete_seal(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v3-evaluation-test", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            run_protocol_v3(
                ROOT / "verify/blind_selector_v3.json", selector_input, output
            )
            seal, states = verify_v3_seal(
                ROOT / "verify/blind_selector_v3.json", output
            )
            self.assertEqual(seal["run_id"], "v3-evaluation-test")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v3(
                ROOT / "verify/blind_selector_v3.json", output,
                output / "prediction.pdb", temporary / "evaluation.json"
            )
            self.assertEqual(evidence["schema"], "fold-protein-blind-evaluation/v3")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
