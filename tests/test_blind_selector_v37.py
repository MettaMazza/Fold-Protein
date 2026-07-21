import unittest

from tools.blind_24_lattice_selector_v37 import select_state_path_v37


UBIQUITIN = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"


class BlindSelectorV37Tests(unittest.TestCase):
    def test_l76_partition_selects_one_complete_chain_candidate(self):
        result = select_state_path_v37(UBIQUITIN)
        self.assertEqual(result["complete_chain_candidates"], 16)
        self.assertEqual(result["partition_span"], 5)
        self.assertEqual(result["partition_unit_count"], 15)
        self.assertEqual(result["expected_unordered_mode_census"], [30, 45])
        self.assertEqual(result["qualifying_candidates"], 1)
        self.assertEqual(sum(row["qualifies"] for row in result["census_trace"]), 1)

    def test_l76_replay_is_deterministic_and_target_incapable(self):
        first = select_state_path_v37(UBIQUITIN)
        second = select_state_path_v37(UBIQUITIN)
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["census_trace"], second["census_trace"])
        self.assertEqual(first["selected_direction"], "n_to_c")
        self.assertEqual(sorted((first["modes"].count("alpha"), first["modes"].count("beta"))), [30, 45])

    def test_nonclosing_active_length_halts(self):
        with self.assertRaises(RuntimeError):
            select_state_path_v37("MQIFVKTL")


if __name__ == "__main__":
    unittest.main()
