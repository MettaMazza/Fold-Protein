import unittest

from tools.verify_protein_selector_v35_generalisation import verify_generalisation


class ProteinSelectorV35GeneralisationTests(unittest.TestCase):
    def test_paired_panel_scores_and_artifacts_are_source_bound(self):
        receipt = verify_generalisation()
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["verified_predictions"], 4)
        self.assertEqual(receipt["proteins_with_tm_improvement"], 2)
        self.assertEqual(receipt["proteins_with_ca_drmsd_improvement"], 2)


if __name__ == "__main__":
    unittest.main()
