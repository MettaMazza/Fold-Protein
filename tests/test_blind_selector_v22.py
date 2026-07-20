import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13 import generated_local_relations_v13
from tools.blind_24_lattice_selector_v22 import (
    HARD_EXCLUSION_STRATA, generated_local_relations_v22,
    generated_prefix_relations_v22)
from tools.blind_24_lattice_selector_v3 import build_lookahead_prefix
from tools.sidechain_graph_contact_topology_v2 import (
    CONTACT_DEFICIT_CENSUS, sidechain_graph_contact_deficit_relation)


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV22Tests(unittest.TestCase):
    def test_contact_deficit_is_exact_complement(self):
        sequence = "MQIFVK"
        path = [0, 1, 2, 3, 4]
        atoms = build_lookahead_prefix(sequence, path)
        row = sidechain_graph_contact_deficit_relation(sequence, atoms)
        self.assertEqual(
            row["contact_deficit"],
            row["possible_atom_pair_count"] - row["atom_contact_count"])
        self.assertGreaterEqual(row["contact_deficit"], 0)
        self.assertIsNone(CONTACT_DEFICIT_CENSUS["target_contact_count"])

    def test_global_hierarchy_contains_contact_deficit(self):
        sequence = "MQIFVK"
        path = [0, 1, 2, 3, 4]
        atoms = build_lookahead_prefix(sequence, path)
        contact = sidechain_graph_contact_deficit_relation(sequence, atoms)
        relation = generated_prefix_relations_v22(sequence, path)
        self.assertEqual(HARD_EXCLUSION_STRATA[-1], "sidechain_contact_deficit")
        self.assertEqual(relation[0][-1], contact["contact_deficit"])

    def test_local_route_remains_exact_v13_with_empty_children(self):
        sequence = "MQIFVK"
        path = [0, 1, 2, 3, 4]
        local = generated_local_relations_v22(sequence, path)
        v13 = generated_local_relations_v13(sequence, path)
        self.assertEqual(local, (v13[0], (v13[1], 0, 0), *v13[2:]))

    def test_import_closure_is_target_incapable(self):
        for relative in (
                "tools/blind_24_lattice_selector_v22.py",
                "tools/sidechain_graph_contact_topology_v2.py"):
            source = (ROOT / relative).read_text().lower()
            self.assertNotIn("1ubq", source)
            self.assertNotIn("calculate_tm", source)
            self.assertNotIn("biopython", source)


if __name__ == "__main__":
    unittest.main()
