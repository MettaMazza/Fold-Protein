import unittest

from tools.blind_24_lattice_selector_v36 import (
    BOUNDARY_CONTEXTS,
    COMPLETE_CHAIN_CANDIDATES,
    DIRECTIONS,
    select_state_path_v36,
)


class BlindSelectorV36Tests(unittest.TestCase):
    def test_both_boundaries_supply_every_complete_context(self):
        result = select_state_path_v36("MQIFVKTL")
        self.assertEqual(result["chain_boundaries"], 2)
        self.assertEqual(result["boundary_contexts"], 8)
        self.assertEqual(result["complete_chain_candidates"], 16)
        self.assertEqual(COMPLETE_CHAIN_CANDIDATES, 16)
        self.assertEqual(
            result["candidates_per_boundary"],
            {direction: BOUNDARY_CONTEXTS for direction in DIRECTIONS},
        )
        self.assertEqual(len(result["reconciliation_trace"]), 16)

    def test_reconciliation_is_deterministic_and_inside_closed_domain(self):
        first = select_state_path_v36("MQIFVKTL")
        second = select_state_path_v36("MQIFVKTL")
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["reconciliation_trace"], second["reconciliation_trace"])
        self.assertEqual(first["selected_direction"], second["selected_direction"])
        domain = set(first["closed_domain"].values())
        self.assertTrue(all(state in domain for state in first["states"][:-1]))

    def test_shorter_than_complete_boundary_halts(self):
        with self.assertRaises(ValueError):
            select_state_path_v36("MQI")


if __name__ == "__main__":
    unittest.main()
