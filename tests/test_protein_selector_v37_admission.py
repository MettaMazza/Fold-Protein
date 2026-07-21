import unittest

from tools.verify_protein_selector_v37_admission import verify_selector_v37_admission


class ProteinSelectorV37AdmissionTests(unittest.TestCase):
    def test_v37_whole_chain_partition_is_admitted(self):
        receipt = verify_selector_v37_admission()
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["active_state_count"], 75)
        self.assertEqual(receipt["expected_unordered_mode_census"], [30, 45])
        self.assertEqual(receipt["complete_chain_candidates"], 16)
        self.assertEqual(receipt["qualifying_candidates"], 1)
        self.assertTrue(receipt["deterministic_replay"])


if __name__ == "__main__":
    unittest.main()
