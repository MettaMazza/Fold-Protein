import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_protocol_v36 import run_protocol_v36
from verify.evaluate_sealed_blind_v36 import verify_v36_seal


ROOT = Path(__file__).resolve().parents[1]


class BlindProtocolV36Tests(unittest.TestCase):
    def test_protocol_seals_complete_two_boundary_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            input_path = temporary / "input.json"
            input_path.write_text(json.dumps({
                "run_id": "v36-test", "sequence": "MQIFVKTL",
            }))
            output = temporary / "sealed"
            run_protocol_v36(ROOT / "verify/blind_selector_v36.json",
                             input_path, output)
            seal, states = verify_v36_seal(
                ROOT / "verify/blind_selector_v36.json", output)
            self.assertEqual(seal["chain_boundaries"], 2)
            self.assertEqual(seal["complete_chain_candidates"], 16)
            self.assertEqual(len(states["reconciliation_trace"]), 16)
            self.assertEqual(set(states["candidates_per_boundary"].values()), {8})


if __name__ == "__main__":
    unittest.main()
