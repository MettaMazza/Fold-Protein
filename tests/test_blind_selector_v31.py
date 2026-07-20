import unittest

from tools.blind_24_lattice_selector_v31 import select_state_path_v31
from tools.tertiary_segment_body_constitution_v3 import (
    DEGREE_FRONTIER, verify_tertiary_topology_frontier)


class BlindSelectorV31Tests(unittest.TestCase):
    def test_counted_degree_frontier_is_complete(self):
        sequence = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQD"
        census = verify_tertiary_topology_frontier(sequence)
        self.assertEqual(tuple(census["degree_frontier"]), DEGREE_FRONTIER)
        self.assertTrue(census["frontier_complete"])
        self.assertEqual([max(row["body_degrees"])
                          for row in census["topologies"]], [2, 3, 4])
        self.assertIsNone(census["target"])

    def test_all_topologies_enter_reconciliation(self):
        sequence = "MQIFVKTLTGKT"
        domains = [{"residue": residue + 1, "expanded_state_count": 576,
                    "retained_states": list(range(24))}
                   for residue in range(len(sequence) - 1)]
        branches = [[state] * (len(sequence) - 1) + [0]
                    for state in range(6)]
        result = select_state_path_v31(sequence, *branches, domain_trace=domains)
        self.assertEqual([row["degree_capacity"]
                          for row in result["topology_traces"]], [2, 3, 4])
        self.assertTrue(all(row["retained_paths"] == 24
                            for row in result["topology_traces"]))
        self.assertEqual(result["states"][-1], 0)


if __name__ == "__main__":
    unittest.main()
