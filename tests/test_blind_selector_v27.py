import unittest

from tools.blind_24_lattice_selector_v27 import (
    _complete_branch_cube, select_state_path_v27)


class BlindSelectorV27Tests(unittest.TestCase):
    def test_complete_binary_branch_cube_seeds_bidirectional_search(self):
        left = (0, 0, 0, 0, 0, 0)
        right = (1, 0, 2, 0, 0, 0)
        cube, differences = _complete_branch_cube(left, right)
        self.assertEqual(differences, (0, 2))
        self.assertEqual(len(cube), 4)
        sequence = "MQIFVK"
        domains = [{
            "residue": residue + 1,
            "expanded_state_count": 576,
            "retained_states": list(range(24)),
        } for residue in range(len(sequence) - 1)]
        result = select_state_path_v27(sequence, left, right, domains)
        self.assertEqual(result["branch_cube"]["complete_candidate_count"], 4)
        self.assertEqual({row["direction"] for row in result["assembly_trace"]},
                         {"forward", "reverse"})
        self.assertEqual(len(result["states"]), len(sequence))


if __name__ == "__main__":
    unittest.main()
