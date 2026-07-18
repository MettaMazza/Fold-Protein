import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.blind_24_lattice_selector_v2 import (
    SelectorV2Config,
    dimensionless_topology_key,
    select_state_path_v2,
)
from tools.run_blind_protocol_v2 import run_protocol_v2


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verify/blind_selector_v2.json"


class BlindProtocolV2Tests(unittest.TestCase):
    def test_key_has_no_external_length_or_reward_parameter(self):
        config = SelectorV2Config()
        self.assertEqual(set(config.__dict__), {"beam_width"})
        ca = np.asarray([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                         [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]])
        key = dimensionless_topology_key("VVVV", ca)
        self.assertEqual(len(key), 3)
        self.assertTrue(all(np.isfinite(value) for value in key))

    def test_selector_v2_is_deterministic(self):
        config = SelectorV2Config(beam_width=2)
        first = select_state_path_v2("ACD", config)
        second = select_state_path_v2("ACD", config)
        self.assertEqual(first["states"], second["states"])
        self.assertEqual(first["score_trace"], second["score_trace"])

    def test_v2_seal_is_target_isolated_and_immutable(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            manifest = json.loads(MANIFEST.read_text())
            manifest["selector_config"]["beam_width"] = 2
            manifest_path = temp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            selector_input = temp / "input.json"
            selector_input.write_text('{"run_id":"v2-test","sequence":"ACD"}\n')
            output = temp / "sealed"
            seal = run_protocol_v2(manifest_path, selector_input, output)
            self.assertEqual(seal["schema"], "fold-protein-blind-seal/v2")
            self.assertEqual(seal["execution"], "sequence-only selector output")
            with self.assertRaises(FileExistsError):
                run_protocol_v2(manifest_path, selector_input, output)

    def test_manifest_records_exact_operational_route(self):
        manifest = json.loads(MANIFEST.read_text())
        self.assertIsNone(manifest["score"]["angstrom_cutoff"])
        self.assertIsNone(manifest["score"]["reward_scale"])
        self.assertEqual(manifest["component_routes"]["dimensionless_topology_order"],
                         "generated-geometry ordering")


if __name__ == "__main__":
    unittest.main()
