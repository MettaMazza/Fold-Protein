import unittest

from tools.verify_protein_engine_closure import verify_engine_closure


class ProteinEngineClosureTests(unittest.TestCase):
    def test_closed_relations_and_unique_angle_forms_execute(self):
        result = verify_engine_closure()
        self.assertEqual(result["status"], "verified")
        self.assertEqual(
            result["angle_candidate_counts"],
            {
                "homochiral_chart_sign": 1,
                "opposite_chart_sign": 1,
                "right_handed_alpha_phi": 1,
                "right_handed_alpha_psi": 1,
                "beta_phi": 1,
                "beta_psi": 1,
            },
        )
        self.assertEqual(
            result["executed"]["verify/protein_angle_form_admission.c"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
