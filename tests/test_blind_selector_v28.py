import unittest

from tools.blind_24_lattice_selector_v28 import select_state_path_v28


class BlindSelectorV28Tests(unittest.TestCase):
    def test_multiscale_bidirectional_branch_propagation(self):
        sequence = "MQIFVKTLT"
        domains = []
        for index in range(len(sequence) - 1):
            domains.append({
                "residue": index + 1,
                "expanded_state_count": 576,
                "retained_states": list(range(24)),
            })
        v25 = [0] * len(sequence)
        v261 = [1] * (len(sequence) - 1) + [0]
        v27 = [2] * (len(sequence) - 1) + [0]
        result = select_state_path_v28(sequence, v25, v261, v27, domains)
        self.assertEqual(result["scales"], [4, 8])
        self.assertEqual(len(result["scale_trace"]), 2)
        self.assertEqual(result["scale_trace"][0]["block_count"], 2)
        self.assertTrue(all(
            stage["forward"] and stage["reverse"]
            for stage in result["scale_trace"]))
        self.assertTrue(all(
            row["retained_paths"] == 24
            for stage in result["scale_trace"]
            for row in stage["forward"] + stage["reverse"]))
        self.assertEqual(len(result["states"]), len(sequence))
        self.assertEqual(result["states"][-1], 0)


if __name__ == "__main__":
    unittest.main()
