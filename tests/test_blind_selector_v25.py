import unittest

from tools.blind_24_lattice_selector_v25 import (
    _coordinate_candidates, select_state_path_v25)


class BlindSelectorV25Tests(unittest.TestCase):
    def test_one_coordinate_basis_and_bidirectional_complete_chain_beam(self):
        sequence = "MQIFVK"
        domains = [{
            "residue": residue + 1,
            "expanded_state_count": 576,
            "retained_states": list(range(24)),
        } for residue in range(len(sequence) - 1)]
        seed = tuple([0] * len(sequence))
        candidates = _coordinate_candidates(seed, (0, 1, 2, 3),
                                             tuple(tuple(range(24)) for _ in range(5)))
        self.assertEqual(len(candidates), 1 + 4 * 23)
        self.assertTrue(all(sum(a != b for a, b in zip(seed, path)) <= 1
                            for path in candidates))
        result = select_state_path_v25(sequence, seed, domains)
        self.assertEqual({row["direction"] for row in result["assembly_trace"]},
                         {"forward", "reverse"})
        self.assertTrue(all(row["retained_paths"] == 24
                            for row in result["assembly_trace"]))
        self.assertEqual(len(result["states"]), len(sequence))


if __name__ == "__main__":
    unittest.main()
