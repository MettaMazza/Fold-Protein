import unittest
from tools.verify_protein_selector_v41_admission import verify_selector_v41_admission


class ProteinSelectorV41AdmissionTests(unittest.TestCase):
    def test_v41_complete_component_cube_is_admitted(self):
        row = verify_selector_v41_admission()
        self.assertEqual(row["status"], "verified")
        self.assertEqual(row["disagreement_count"], 42)
        self.assertEqual(row["component_count"], 13)
        self.assertEqual(row["component_cube_candidates"], 8192)
        self.assertTrue(row["parents_in_cube"])


if __name__ == "__main__": unittest.main()
