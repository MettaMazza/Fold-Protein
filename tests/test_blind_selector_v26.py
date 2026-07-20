import unittest

from tools.blind_24_lattice_selector_v26 import select_state_path_v26


class BlindSelectorV26Tests(unittest.TestCase):
    def test_joint_topology_expands_full_paired_domains(self):
        sequence = "MQIFVKTL"
        domains = [{
            "residue": residue + 1,
            "expanded_state_count": 576,
            "retained_states": list(range(24)),
        } for residue in range(len(sequence) - 1)]
        result = select_state_path_v26(sequence, [0] * len(sequence), domains)
        self.assertGreater(len(result["topology_trace"]), 0)
        self.assertTrue(all(row["paired_state_count_per_residue_pair"] == 576
                            for row in result["topology_trace"]))
        self.assertTrue(all(row["retained_paths"] == 24
                            for row in result["topology_trace"]))
        self.assertEqual({row["direction"] for row in result["assembly_trace"]},
                         {"forward", "reverse"})
        self.assertEqual(len(result["states"]), len(sequence))


if __name__ == "__main__":
    unittest.main()
