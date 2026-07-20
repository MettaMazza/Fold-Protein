import unittest

from tools.blind_24_lattice_selector_v29 import select_state_path_v29


class BlindSelectorV29Tests(unittest.TestCase):
    def test_joint_tertiary_body_topology_executes(self):
        sequence = "MQIFVKTLTGKT"
        domains = [{
            "residue": residue + 1,
            "expanded_state_count": 576,
            "retained_states": list(range(24)),
        } for residue in range(len(sequence) - 1)]
        branches = []
        for state in range(4):
            branches.append([state] * (len(sequence) - 1) + [0])
        result = select_state_path_v29(
            sequence, *branches, domain_trace=domains)
        self.assertEqual(result["tertiary_census"]["segment_count"], 3)
        self.assertEqual(result["tertiary_census"]["tree_edge_count"], 2)
        self.assertEqual(len(result["assembly_trace"]), 4)
        self.assertTrue(all(
            row["retained_paths"] == 24 for row in result["assembly_trace"]))
        self.assertEqual(result["states"][-1], 0)


if __name__ == "__main__":
    unittest.main()
