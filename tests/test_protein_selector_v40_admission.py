import unittest

from tools.verify_protein_selector_v40_admission import verify_selector_v40_admission


class ProteinSelectorV40AdmissionTests(unittest.TestCase):
    def test_v40_complete_lineage_paired_state_form_is_admitted(self):
        receipt = verify_selector_v40_admission()
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["lineage_seed_count"], 2)
        self.assertEqual(receipt["paired_state_count"], 576)
        self.assertEqual(receipt["updates_per_residue_across_lineage"], 1152)
        self.assertEqual(receipt["causal_direction"], "n_to_c")
        self.assertTrue(receipt["paired_scan_exhaustive"])


if __name__ == "__main__":
    unittest.main()
