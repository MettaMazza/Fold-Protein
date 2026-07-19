import ast
import json
from pathlib import Path
import tempfile
import unittest

from tools.backbone_hydrogen_bond_constitution_v1 import (
    HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation)
from tools.blind_24_lattice_selector_v11 import select_state_path_v11
from tools.run_blind_protocol_v11 import run_protocol_v11
from verify.evaluate_sealed_blind_v11 import evaluate_v11, verify_v11_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV11Tests(unittest.TestCase):
    def test_hydrogen_bond_constitution_closes_without_cutoffs(self):
        self.assertEqual(HYDROGEN_BOND_CENSUS["non_donor_residues"], "P")
        self.assertEqual(HYDROGEN_BOND_CENSUS["donor_capacity"], 1)
        self.assertEqual(HYDROGEN_BOND_CENSUS["acceptor_capacity"], 1)
        self.assertIsNone(HYDROGEN_BOND_CENSUS["distance_cutoff"])
        self.assertIsNone(HYDROGEN_BOND_CENSUS["angular_cutoff"])

    def test_v11_relation_is_active_and_unit_capacity(self):
        result = select_state_path_v11("MQIFVKTL")
        assembly = result["final_relations"]["hydrogen_bond_assembly"]
        self.assertLess(assembly["relation"], 0)
        donors = [row["donor_residue"] for row in assembly["pairs"]]
        acceptors = [row["acceptor_residue"] for row in assembly["pairs"]]
        self.assertEqual(len(donors), len(set(donors)))
        self.assertEqual(len(acceptors), len(set(acceptors)))

    def test_v11_retains_binary_mode_capacity(self):
        result = select_state_path_v11("WGGW")
        self.assertEqual(result["mode_capacity"], 12)
        self.assertEqual(len(result["final_relations"]["objectives"]), 11)
        self.assertEqual(
            len(result["final_relations"]["ordinal_rank_vector"]), 11)
        for row in result["mode_balance_trace"][1:]:
            self.assertEqual(row["alpha"]["retained"], 12)
            self.assertEqual(row["beta"]["retained"], 12)

    def test_v11_is_deterministic(self):
        first = select_state_path_v11("KADKW")
        second = select_state_path_v11("KADKW")
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["final_relations"], second["final_relations"])

    def test_v11_import_closure_is_target_incapable(self):
        for relative in (
            "tools/backbone_hydrogen_bond_constitution_v1.py",
            "tools/blind_24_lattice_selector_v11.py",
            "tools/run_blind_protocol_v11.py",
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

    def test_protocol_seals_and_evaluator_opens_target_after_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v11-test-mq", "sequence": "MQ",
            }))
            output = temporary / "sealed"
            manifest = ROOT / "verify/blind_selector_v11.json"
            seal = run_protocol_v11(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v11")
            checked, states = verify_v11_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v11-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v11(
                manifest, output, output / "prediction.pdb",
                temporary / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
