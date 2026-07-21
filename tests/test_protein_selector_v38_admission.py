import unittest

from tools.verify_protein_selector_v38_admission import verify_selector_v38_admission


class ProteinSelectorV38AdmissionTests(unittest.TestCase):
    def test_v38_complete_coordinate_fixed_point_is_admitted(self):
        receipt = verify_selector_v38_admission()
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["axis_value_count"], 24)
        self.assertEqual(receipt["paired_state_count"], 576)
        self.assertEqual(receipt["descent_order_count"], 4)
        self.assertTrue(receipt["coordinate_scan_exhaustive"])


if __name__ == "__main__":
    unittest.main()
