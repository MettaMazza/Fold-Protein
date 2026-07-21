import unittest

from tools.verify_protein_selector_v36_admission import verify_selector_v36_admission


class ProteinSelectorV36AdmissionTests(unittest.TestCase):
    def test_v36_complete_two_boundary_form_is_admitted(self):
        receipt = verify_selector_v36_admission()
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["chain_boundaries"], 2)
        self.assertEqual(receipt["boundary_contexts"], 8)
        self.assertEqual(receipt["complete_chain_candidates"], 16)


if __name__ == "__main__":
    unittest.main()
