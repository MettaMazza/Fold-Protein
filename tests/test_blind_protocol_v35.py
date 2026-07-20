import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_protocol_v35 import run_protocol_v35
from verify.evaluate_sealed_blind_v35 import verify_v35_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindProtocolV35Tests(unittest.TestCase):
    def test_protocol_seals_complete_boundary_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            input_path = temporary / "input.json"
            input_path.write_text(json.dumps({
                "run_id": "v35-test", "sequence": "MQIFVKTL",
            }))
            output = temporary / "sealed"
            run_protocol_v35(ROOT / "verify/blind_selector_v35.json",
                             input_path, output)
            seal, states = verify_v35_seal(
                ROOT / "verify/blind_selector_v35.json", output)
            self.assertEqual(seal["boundary_contexts"], 8)
            self.assertEqual(seal["quartet_transitions"], 16)
            self.assertTrue(all(row["retained_contexts"] == 8
                                for row in states["boundary_trace"][3:]))


if __name__ == "__main__":
    unittest.main()
