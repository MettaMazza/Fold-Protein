import unittest

from tools.trace_blind_ladder_decisions_v2 import trace_pair


class BlindLadderDecisionTraceV2Tests(unittest.TestCase):
    def test_trace_excludes_final_canonical_state_and_records_relation(self):
        shared = [{"active_state": index} for index in range(3)]
        row = trace_pair(
            {"sequence": "AAAA", "states": [0, 1, 2, 0],
             "score_trace": shared},
            {"sequence": "AAAAA", "states": [0, 1, 3, 4, 0],
             "score_trace": shared + [{"active_state": 3}]},
        )
        self.assertEqual(row["active_states_compared"], 3)
        self.assertEqual(row["changed_state_count"], 1)
        self.assertEqual(row["first_divergence_zero_based"], 2)
        self.assertTrue(row["shared_frontier_trace_identical"])
        self.assertIn("short_angles_radians", row["changed_states"][0])
        self.assertIn(row["changed_states"][0]["topology_key_relation_at_prefix"], {
            "shorter-path-prefix-first", "longer-path-prefix-first",
            "equal-topology-key"})
        self.assertIn(row["changed_states"][0]["full_selection_relation_at_prefix"], {
            "shorter-path-prefix-first", "longer-path-prefix-first"})

    def test_nonprefix_sequence_halts(self):
        with self.assertRaisesRegex(ValueError, "does not extend"):
            trace_pair(
                {"sequence": "AAAA", "states": [0, 0, 0, 0]},
                {"sequence": "BAAAA", "states": [0, 0, 0, 0, 0]},
            )


if __name__ == "__main__":
    unittest.main()
