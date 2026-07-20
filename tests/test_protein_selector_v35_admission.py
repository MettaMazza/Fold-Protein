import unittest

from tools.verify_protein_selector_v35_admission import (
    verify_selector_v35_admission)


class ProteinSelectorV35AdmissionTests(unittest.TestCase):
    def test_v35_complete_boundary_graph_is_admitted(self):
        result = verify_selector_v35_admission()
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["boundary_contexts"], 8)
        self.assertEqual(result["quartet_transitions"], 16)
        self.assertTrue(result["deterministic_replay"])


if __name__ == "__main__":
    unittest.main()
