import unittest

from tools.blind_24_lattice_selector_v35 import (
    BOUNDARY_CONTEXTS,
    QUARTET_TRANSITIONS,
    select_state_path_v35,
)


class BlindSelectorV35Tests(unittest.TestCase):
    def test_complete_boundary_graph_is_propagated(self):
        result = select_state_path_v35("MQIFVKTL")
        trace = result["boundary_trace"]
        self.assertEqual(BOUNDARY_CONTEXTS, 8)
        self.assertEqual(QUARTET_TRANSITIONS, 16)
        self.assertEqual([row["retained_contexts"] for row in trace[:3]], [2, 4, 8])
        self.assertTrue(all(row["retained_contexts"] == 8 for row in trace[3:]))
        self.assertTrue(all(row["expanded_transitions"] == 16 for row in trace[3:]))
        self.assertEqual(trace[2]["inbound_per_context"], [1])
        self.assertTrue(all(row["inbound_per_context"] == [2] for row in trace[3:]))

    def test_output_is_deterministic_and_inside_closed_domain(self):
        first = select_state_path_v35("MQIFVKTL")
        second = select_state_path_v35("MQIFVKTL")
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["boundary_trace"], second["boundary_trace"])
        domain = set(first["closed_domain"].values())
        self.assertTrue(all(state in domain for state in first["states"][:-1]))
        self.assertEqual(first["states"][-1], 0)


if __name__ == "__main__":
    unittest.main()
