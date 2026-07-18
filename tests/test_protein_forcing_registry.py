import unittest

from tools.verify_protein_forcing_registry import verify_registry


class ProteinForcingRegistryTests(unittest.TestCase):
    def test_every_source_is_classified_and_v3_has_clean_closure(self):
        receipt = verify_registry()
        self.assertEqual(receipt["status"], "verified")
        self.assertGreater(receipt["classified_sources"], 50)
        self.assertEqual(
            receipt["history_floor_commit"],
            "6b08f5288034d0958a15c8b4b0af0edb59715e37",
        )
        self.assertEqual(receipt["inherited_compiler"]["tracked_files"], 315)


if __name__ == "__main__":
    unittest.main()
