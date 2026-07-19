import ast
import json
import tempfile
import unittest
from pathlib import Path

from tools.backbone_hydrogen_bond_constitution_v2 import (
    TOPOLOGY_HYDROGEN_BOND_CENSUS,
    topology_backbone_hydrogen_bond_relation)
from tools.blind_24_lattice_selector_v12 import select_state_path_v12
from tools.run_blind_protocol_v12 import run_protocol_v12
from verify.evaluate_sealed_blind_v12 import evaluate_v12, verify_v12_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV12Tests(unittest.TestCase):
    def test_topology_constitution_has_no_cutoff_or_weight(self):
        census = TOPOLOGY_HYDROGEN_BOND_CENSUS
        self.assertEqual(census["alpha_sequence_separation"], 4)
        self.assertEqual(census["interstrand_minimum_separation"], 5)
        self.assertEqual(census["topology_classes"], ["alpha", "interstrand"])
        self.assertEqual(census["global_donor_capacity"], 1)
        self.assertEqual(census["global_acceptor_capacity"], 1)
        self.assertIsNone(census["distance_cutoff"])
        self.assertIsNone(census["angular_cutoff"])
        self.assertIsNone(census["topology_weight"])

    def test_exact_alpha_topology_and_global_capacity(self):
        result = select_state_path_v12("MQIFVKTL")
        assembly = result["final_relations"]["hydrogen_bond_topologies"]
        donors = [row["donor_residue"] for row in assembly["pairs"]]
        acceptors = [row["acceptor_residue"] for row in assembly["pairs"]]
        self.assertEqual(len(donors), len(set(donors)))
        self.assertEqual(len(acceptors), len(set(acceptors)))
        for row in assembly["pairs"]:
            if row["topology"] == "alpha":
                self.assertEqual(
                    row["donor_residue"] - row["acceptor_residue"], 4)
            else:
                self.assertGreater(row["sequence_separation"], 4)

    def test_v12_relation_is_active_and_complete(self):
        result = select_state_path_v12("MQIFVKTL")
        self.assertEqual(len(result["states"]), 8)
        self.assertEqual(len(result["final_relations"]["objectives"]), 13)
        self.assertEqual(
            len(result["final_relations"]["ordinal_rank_vector"]), 13)
        assembly = result["final_relations"]["hydrogen_bond_topologies"]
        self.assertGreater(assembly["eligible_pair_count"], 0)
        self.assertGreater(assembly["pair_count"], 0)

    def test_v12_is_deterministic(self):
        first = select_state_path_v12("KADKW")
        second = select_state_path_v12("KADKW")
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["final_relations"], second["final_relations"])

    def test_v12_import_closure_is_target_incapable(self):
        for relative in (
            "tools/backbone_hydrogen_bond_constitution_v2.py",
            "tools/blind_24_lattice_selector_v12.py",
        ):
            source = (ROOT / relative).read_text().lower()
            tree = ast.parse(source)
            for prohibited in (
                    "parse_pdb", "target_pdb", "optimize_empirical", "compute_tm"):
                self.assertNotIn(prohibited, source)
            imported = {
                node.module for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module}
            self.assertNotIn("calculate_tm", imported)

    def test_short_relation_has_closed_zero_evidence(self):
        result = select_state_path_v12("MQIF")
        assembly = topology_backbone_hydrogen_bond_relation(
            "MQIF", result["atoms"])
        self.assertEqual(assembly["pair_count"], 0)
        self.assertEqual(assembly["relations"], {
            "alpha": 0.0, "interstrand": 0.0})

    def test_v12_seals_before_target_evaluation(self):
        with tempfile.TemporaryDirectory() as held:
            root = Path(held)
            selector_input = root / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v12-test-mq", "sequence": "MQ"}))
            output = root / "sealed"
            manifest = ROOT / "verify/blind_selector_v12.json"
            seal = run_protocol_v12(manifest, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v12")
            checked, states = verify_v12_seal(manifest, output)
            self.assertEqual(checked["run_id"], "v12-test-mq")
            self.assertEqual(states["sequence"], "MQ")
            evidence = evaluate_v12(
                manifest, output, output / "prediction.pdb",
                root / "evaluation.json")
            self.assertAlmostEqual(evidence["tm_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
