import unittest

from tools.blind_24_lattice_selector_v26_1 import select_state_path_v26_1


class BlindSelectorV261Tests(unittest.TestCase):
    def test_focal_admission_precedes_complete_chain_balance(self):
        sequence = "MQIFVKTL"
        domains = [{
            "residue": residue + 1,
            "expanded_state_count": 576,
            "retained_states": list(range(24)),
        } for residue in range(len(sequence) - 1)]
        result = select_state_path_v26_1(sequence, [0] * len(sequence), domains)
        self.assertGreater(len(result["topology_trace"]), 0)
        self.assertTrue(all(row["focally_admitted_paths"]
                            == row["residue_pair_count"] * 24
                            for row in result["topology_trace"]))
        self.assertTrue(all(row["retained_paths"] == 24
                            for row in result["topology_trace"]))
        self.assertGreater(result["focal_evaluations"], 0)


if __name__ == "__main__":
    unittest.main()
