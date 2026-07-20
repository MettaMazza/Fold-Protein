import unittest

from tools.blind_24_lattice_selector_v30 import select_state_path_v30
from tools.tertiary_segment_body_constitution_v2 import (
    build_tertiary_segment_path, verify_tertiary_segment_path_constitution)


class BlindSelectorV30Tests(unittest.TestCase):
    def test_sequence_topology_is_a_degree_two_path(self):
        sequence = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"
        topology = build_tertiary_segment_path(sequence)
        census = verify_tertiary_segment_path_constitution(sequence)
        self.assertEqual(len(topology), census["segment_count"] - 1)
        self.assertLessEqual(max(census["body_degrees"]), 2)
        self.assertEqual(sum(census["body_degrees"]), 2 * len(topology))
        self.assertIsNone(census["target"])

    def test_joint_tertiary_path_executes(self):
        sequence = "MQIFVKTLTGKT"
        domains = [{"residue": residue + 1, "expanded_state_count": 576,
                    "retained_states": list(range(24))}
                   for residue in range(len(sequence) - 1)]
        branches = [[state] * (len(sequence) - 1) + [0]
                    for state in range(4)]
        result = select_state_path_v30(sequence, *branches, domain_trace=domains)
        self.assertEqual(result["tertiary_census"]["path_edge_count"], 2)
        self.assertTrue(result["tertiary_census"]["connected_acyclic_degree_two"])
        self.assertEqual(len(result["assembly_trace"]), 4)
        self.assertEqual(result["states"][-1], 0)


if __name__ == "__main__":
    unittest.main()
