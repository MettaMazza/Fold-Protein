import json
from pathlib import Path
import tempfile
import unittest

from tools.blind_24_lattice_selector_v34 import (
    closed_angle_domain, select_state_path_v34)
from tools.run_blind_protocol_v34 import run_protocol_v34
from verify.evaluate_sealed_blind_v34 import verify_v34_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV34Tests(unittest.TestCase):
    def test_closed_domain_is_exactly_the_two_v2_forms(self):
        self.assertEqual(closed_angle_domain(), {"alpha": 201, "beta": 117})

    def test_every_active_residue_enumerates_the_complete_domain(self):
        result = select_state_path_v34("MQIFVK")
        domain = set(result["closed_domain"].values())
        self.assertTrue(all(state in domain for state in result["states"][:-1]))
        self.assertEqual(result["states"][-1], 0)
        self.assertTrue(all(row["candidate_domain"] == sorted(domain)
                            for row in result["score_trace"]))
        self.assertEqual([row["expanded"] for row in result["score_trace"]],
                         [2, 4, 8, 16, 32])

    def test_protocol_seals_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            selector_input = temporary / "input.json"
            selector_input.write_text(json.dumps({
                "run_id": "v34-test", "sequence": "MQIF",
            }))
            output = temporary / "sealed"
            run_protocol_v34(ROOT / "verify/blind_selector_v34.json",
                             selector_input, output)
            seal, states = verify_v34_seal(
                ROOT / "verify/blind_selector_v34.json", output)
            self.assertEqual(seal["path_length"], 4)
            self.assertEqual(states["closed_domain"], {"alpha": 201, "beta": 117})
            state_record = json.loads((output / "selected_states.json").read_text())
            state_record["states"][0] = 0
            (output / "selected_states.json").write_text(json.dumps(state_record))
            with self.assertRaisesRegex(RuntimeError, "seal mismatch"):
                verify_v34_seal(ROOT / "verify/blind_selector_v34.json", output)


if __name__ == "__main__":
    unittest.main()
