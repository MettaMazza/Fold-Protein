import unittest

from tools.verify_protein_selector_v34_admission import (
    verify_selector_v34_admission)


class ProteinSelectorV34AdmissionTests(unittest.TestCase):
    def test_v34_composition_is_closed_and_target_free(self):
        result = verify_selector_v34_admission()
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["candidate_domain"], {"alpha": 201, "beta": 117})
        self.assertTrue(result["deterministic_replay"])


if __name__ == "__main__":
    unittest.main()
