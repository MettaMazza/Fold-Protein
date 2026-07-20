import unittest

from tools.verify_protein_derivation_admission import verify_admission


class ProteinDerivationAdmissionTests(unittest.TestCase):
    def test_open_selector_forms_cannot_enter_active_forcing(self):
        result = verify_admission()
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["open_selector_range"], "V4-V33 development-only")
        self.assertEqual(result["required_derivation_guards"], 7)


if __name__ == "__main__":
    unittest.main()
