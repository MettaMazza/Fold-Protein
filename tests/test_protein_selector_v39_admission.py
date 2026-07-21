import unittest

from tools.verify_protein_selector_v39_admission import verify_selector_v39_admission


class ProteinSelectorV39AdmissionTests(unittest.TestCase):
    def test_v39_peptide_causal_fixed_point_is_admitted(self):
        receipt = verify_selector_v39_admission()
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["parent_fixed_points"], 4)
        self.assertEqual(receipt["causal_direction"], "n_to_c")
        self.assertEqual(receipt["causal_axis_order"], [0, 1])
        self.assertEqual(receipt["qualifying_fixed_points"], 1)
        self.assertTrue(receipt["deterministic_replay"])


if __name__ == "__main__":
    unittest.main()
