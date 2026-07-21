import json
from pathlib import Path
import tempfile
import unittest

from tools.run_blind_protocol_v37 import run_protocol_v37
from verify.evaluate_sealed_blind_v37 import verify_v37_seal


ROOT = Path(__file__).resolve().parents[1]
UBIQUITIN = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"


class BlindProtocolV37Tests(unittest.TestCase):
    def test_protocol_seals_unique_whole_chain_partition(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            input_path = temporary / "input.json"
            input_path.write_text(json.dumps({
                "run_id": "v37-test", "sequence": UBIQUITIN,
            }))
            output = temporary / "sealed"
            run_protocol_v37(ROOT / "verify/blind_selector_v37.json",
                             input_path, output)
            seal, states = verify_v37_seal(
                ROOT / "verify/blind_selector_v37.json", output)
            self.assertEqual(seal["complete_chain_candidates"], 16)
            self.assertEqual(seal["partition_unit_count"], 15)
            self.assertEqual(seal["expected_unordered_mode_census"], [30, 45])
            self.assertEqual(seal["qualifying_candidates"], 1)
            self.assertEqual(sum(row["qualifies"] for row in states["census_trace"]), 1)


if __name__ == "__main__":
    unittest.main()
