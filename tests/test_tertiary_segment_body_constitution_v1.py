import unittest

from tools.blind_24_lattice_selector_v23 import _atoms_for_states
from tools.tertiary_segment_body_constitution_v1 import (
    build_tertiary_segment_topology, tertiary_segment_body_relation,
    verify_tertiary_segment_body_constitution)


class TertiarySegmentBodyConstitutionTests(unittest.TestCase):
    def test_sequence_only_topology_closes_to_tree(self):
        sequence = "MQIFVKTLTGKTITLE"
        topology = build_tertiary_segment_topology(sequence)
        self.assertEqual(len(topology), 3)
        self.assertEqual(
            verify_tertiary_segment_body_constitution(sequence)["tree_edge_count"], 3)
        self.assertTrue(all("ordinal_vector" in edge for edge in topology))

    def test_generated_relation_is_target_free_and_complete(self):
        sequence = "MQIFVKTLTGKTITLE"
        atoms = _atoms_for_states(sequence, tuple([0] * len(sequence)))
        relation = tertiary_segment_body_relation(sequence, atoms)
        self.assertEqual(len(relation["edges"]), 3)
        self.assertEqual(len(relation["objectives"]), 8)
        census = verify_tertiary_segment_body_constitution(sequence)
        self.assertIsNone(census["target"])
        self.assertIsNone(census["weight"])


if __name__ == "__main__":
    unittest.main()
