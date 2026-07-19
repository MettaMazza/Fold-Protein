import ast
import json
import tempfile
import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13 import (
    generated_local_relations_v13, generated_prefix_relations_v13,
    select_state_path_v13)
from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_local_relations_v13_single_build,
    generated_prefix_relations_v13_single_build,
    select_state_path_v13_single_build)
from tools.blind_24_lattice_selector_v11 import generated_local_relations_v11
from tools.blind_24_lattice_selector_v12 import generated_local_relations_v12
from tools.run_blind_protocol_v13 import run_protocol_v13
from verify.evaluate_sealed_blind_v13 import evaluate_v13, verify_v13_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV13Tests(unittest.TestCase):
    def test_both_hydrogen_bond_constitutions_are_active(self):
        result = select_state_path_v13("MQIFVKTL")
        self.assertEqual(len(result["states"]), 8)
        self.assertEqual(len(result["final_relations"]["objectives"]), 15)
        self.assertIn("hydrogen_bond_assembly", result["final_relations"])
        self.assertIn("hydrogen_bond_topologies", result["final_relations"])

    def test_local_relation_retains_v11_quartet_beside_v12(self):
        path = [11, 201, 21]
        relations = generated_local_relations_v13("MQIF", path)
        self.assertEqual(relations[:-1], generated_local_relations_v12(
            "MQIF", path))
        self.assertEqual(relations[-1], generated_local_relations_v11(
            "MQIF", path)[-1])

    def test_v13_is_deterministic(self):
        first = select_state_path_v13("KADKW")
        second = select_state_path_v13("KADKW")
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["final_relations"], second["final_relations"])

    def test_single_build_candidate_is_exact(self):
        sequence = "MQIFV"
        for path in ([11], [11, 201], [11, 201, 21], [11, 201, 21, 309]):
            self.assertEqual(
                generated_local_relations_v13(sequence, list(path)),
                generated_local_relations_v13_single_build(
                    sequence, list(path)))
            self.assertEqual(
                generated_prefix_relations_v13(sequence, list(path)),
                generated_prefix_relations_v13_single_build(
                    sequence, list(path)))

        baseline = select_state_path_v13(sequence)
        candidate = select_state_path_v13_single_build(sequence)
        for field in baseline:
            if field != "atoms":
                self.assertEqual(baseline[field], candidate[field])

    def test_v13_import_closure_is_target_incapable(self):
        source = (ROOT / "tools/blind_24_lattice_selector_v13.py").read_text().lower()
        tree = ast.parse(source)
        for prohibited in ("parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
            self.assertNotIn(prohibited, source)
        imported = {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        self.assertNotIn("calculate_tm", imported)

    def test_v13_seals_before_target_evaluation(self):
        with tempfile.TemporaryDirectory() as held:
            root = Path(held)
            selector_input = root / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v13-test-mq", "sequence": "MQ"}))
            output = root / "sealed"
            manifest = ROOT / "verify/blind_selector_v13.json"
            seal = run_protocol_v13(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v13")
            checked, states = verify_v13_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v13-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v13(
                manifest, output, output / "prediction.pdb",
                root / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
