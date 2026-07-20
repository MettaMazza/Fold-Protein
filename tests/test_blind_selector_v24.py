import unittest

from tools.blind_24_lattice_selector_v24 import select_state_path_v24


class BlindSelectorV24Tests(unittest.TestCase):
    def test_coherent_segment_frontiers_precede_bidirectional_assembly(self):
        sequence = "MQIFVK"
        domains = [{
            "residue": residue + 1,
            "expanded_state_count": 576,
            "retained_states": list(range(24)),
        } for residue in range(len(sequence) - 1)]
        result = select_state_path_v24(sequence, [0] * len(sequence), domains)
        self.assertTrue(all(row["retained_tuple_count"] == 24
                            for row in result["segment_generation_trace"]))
        self.assertEqual({row["direction"] for row in result["assembly_trace"]},
                         {"forward", "reverse"})
        self.assertEqual(len(result["states"]), len(sequence))


if __name__ == "__main__":
    unittest.main()
