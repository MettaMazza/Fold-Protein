import unittest

from tools.blind_24_lattice_selector_v32 import (
    _consensus_relation, select_state_path_v32)


class BlindSelectorV32Tests(unittest.TestCase):
    def test_consensus_is_symmetric_across_family_order(self):
        candidate = (0, 0, 0, 0)
        families = (((0, 1, 0, 0),), ((0, 0, 2, 0),), ((3, 0, 0, 0),))
        forward = _consensus_relation(candidate, families)
        reverse = _consensus_relation(candidate, tuple(reversed(families)))
        self.assertEqual(sorted(forward["family_minimum_state_distances"]),
                         sorted(reverse["family_minimum_state_distances"]))
        self.assertEqual(forward["worst_family_distance"], 1)

    def test_cross_topology_consensus_executes(self):
        sequence = "MQIFVKTLTGKT"
        domains = [{"residue": residue + 1, "expanded_state_count": 576,
                    "retained_states": list(range(24))}
                   for residue in range(len(sequence) - 1)]
        branches = [[state] * (len(sequence) - 1) + [0]
                    for state in range(6)]
        result = select_state_path_v32(sequence, *branches, domain_trace=domains)
        self.assertEqual(result["consensus"]["family_order"], [2, 3, 4])
        self.assertEqual(result["consensus"]["retained_paths"], 24)
        self.assertEqual(result["states"][-1], 0)
        self.assertIsNone(result["tertiary_census"]["target"])


if __name__ == "__main__":
    unittest.main()
