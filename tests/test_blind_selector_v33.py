import unittest

from tools.blind_24_lattice_selector_v33 import select_state_path_v33


class BlindSelectorV33Tests(unittest.TestCase):
    def test_exact_minimax_consensus_executes(self):
        sequence = "MQIFVKTLTGKT"
        domains = [{"residue": residue + 1, "expanded_state_count": 576,
                    "retained_states": list(range(24))}
                   for residue in range(len(sequence) - 1)]
        branches = [[state] * (len(sequence) - 1) + [0]
                    for state in range(6)]
        result = select_state_path_v33(sequence, *branches, domain_trace=domains)
        consensus = result["minimax_consensus"]
        self.assertGreater(consensus["minimax_candidate_count"], 0)
        self.assertLessEqual(consensus["retained_paths"], 24)
        self.assertTrue(all(
            row["worst_family_distance"]
            == consensus["minimax_worst_family_distance"]
            for row in consensus["retained_relations"]))
        self.assertEqual(result["states"][-1], 0)
        self.assertIsNone(result["tertiary_census"]["target"])


if __name__ == "__main__":
    unittest.main()
