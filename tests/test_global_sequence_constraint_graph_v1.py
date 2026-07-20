import unittest

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.global_sequence_constraint_graph_v1 import (
    SEGMENT_RESIDUES, build_sequence_constraint_graph,
    sequence_constraint_relations, verify_sequence_constraint_graph)
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates


class GlobalSequenceConstraintGraphTests(unittest.TestCase):
    def test_graph_is_complete_and_sequence_fixed(self):
        sequence = "MQIFVKTL"
        graph = build_sequence_constraint_graph(sequence)
        self.assertEqual(len(graph), sum(range(len(sequence) - 1)))
        self.assertEqual(verify_sequence_constraint_graph(sequence)["segment_residues"], 4)
        self.assertEqual(SEGMENT_RESIDUES, 4)

    def test_relations_are_integer_and_target_free(self):
        sequence = "MQIFVKTL"
        states = [0] * len(sequence)
        phi = [angles_for_state(state)[0] for state in states]
        psi = [angles_for_state(state)[1] for state in states]
        atoms = build_backbone_coordinates(sequence, phi, psi)
        relation = sequence_constraint_relations(sequence, atoms)
        self.assertIsInstance(relation["backbone_exclusions"], int)
        self.assertTrue(all(isinstance(value, int) for value in relation["objectives"]))
        census = verify_sequence_constraint_graph(sequence)
        self.assertIsNone(census["target"])
        self.assertIsNone(census["mixing_weight"])


if __name__ == "__main__":
    unittest.main()
