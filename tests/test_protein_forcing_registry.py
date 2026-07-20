import unittest

from tools.verify_protein_forcing_registry import verify_registry


class ProteinForcingRegistryTests(unittest.TestCase):
    def test_every_source_is_classified_and_active_routes_have_clean_closure(self):
        receipt = verify_registry()
        self.assertEqual(receipt["status"], "verified")
        self.assertGreater(receipt["classified_sources"], 50)
        self.assertEqual(
            receipt["history_floor_commit"],
            "6b08f5288034d0958a15c8b4b0af0edb59715e37",
        )
        self.assertEqual(receipt["inherited_compiler"]["tracked_files"], 315)
        self.assertEqual(receipt["artifact_inventory"]["tracked_pdb_files"], 123)
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"]["sealed_v3_blind_prediction"],
            4,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v5_agent_development_output"],
            2,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v6_v8_agent_development_output"],
            3,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v9_v10_agent_development_output"],
            3,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v12_agent_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v13_cumulative_development_output"],
            3,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v14_continuity_development_output"],
            2,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v15_spatial_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v16_binary_spatial_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v17_graph_spatial_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v18_hierarchical_graph_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v19_global_graph_development_output"],
            3,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v20_graph_atom_hierarchy_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v21_graph_contact_development_output"],
            1,
        )
        self.assertEqual(
            receipt["artifact_inventory"]["class_counts"][
                "sealed_v22_contact_deficit_development_output"],
            1,
        )
        self.assertEqual(receipt["artifact_inventory"]["v2_ladder"]["failed_runs"], 0)
        self.assertEqual(receipt["other_tracked_artifacts"], 3)


if __name__ == "__main__":
    unittest.main()
