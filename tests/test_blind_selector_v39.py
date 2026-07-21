import json
from pathlib import Path
import unittest

from tools.blind_24_lattice_selector_v39 import select_state_path_v39


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "verify/development_runs/ubiquitin_v38_coordinate_fixed_point_l76_20260721/selected_states.json"


class BlindSelectorV39Tests(unittest.TestCase):
    def test_unique_peptide_causal_fixed_point_is_selected(self):
        parent = json.loads(PARENT.read_text())
        result = select_state_path_v39(parent["sequence"], parent)
        self.assertEqual(result["parent_fixed_point_count"], 4)
        self.assertEqual(result["causal_direction"], "n_to_c")
        self.assertEqual(result["causal_axis_order"], [0, 1])
        self.assertEqual(result["causal_event_ranks"], {"phi": 3, "psi": 4})
        self.assertEqual(len(result["states"]), 76)

    def test_incomplete_parent_grammar_halts(self):
        parent = json.loads(PARENT.read_text())
        parent["descent_trace"] = parent["descent_trace"][:-1]
        with self.assertRaises(RuntimeError):
            select_state_path_v39(parent["sequence"], parent)


if __name__ == "__main__":
    unittest.main()
