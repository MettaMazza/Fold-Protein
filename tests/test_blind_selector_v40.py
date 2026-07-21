import unittest

from tools.blind_24_lattice_selector_v40 import (
    CAUSAL_DIRECTION,
    LINEAGE_SEED_COUNT,
    PARALLEL_WORKERS,
    PAIRED_STATE_COUNT,
    _replace_paired_state,
    select_state_path_v40,
)


class BlindSelectorV40Tests(unittest.TestCase):
    def test_complete_lineage_and_paired_state_counts(self):
        self.assertEqual(LINEAGE_SEED_COUNT, 2)
        self.assertEqual(PAIRED_STATE_COUNT, 576)
        self.assertEqual(PARALLEL_WORKERS, 24)
        self.assertEqual(CAUSAL_DIRECTION, "n_to_c")

    def test_paired_replacement_exhausts_complete_lattice(self):
        seed = (14, 201, 0)
        candidates = {
            _replace_paired_state(seed, 1, state)
            for state in range(PAIRED_STATE_COUNT)
        }
        self.assertEqual(len(candidates), 576)
        self.assertTrue(all(row[0] == 14 and row[2] == 0 for row in candidates))

    def test_short_parent_child_lineage_executes_both_seeds(self):
        sequence = "MA"
        v38 = {
            "schema": "fold-protein-selected-states/v38",
            "sequence": sequence,
            "states": [0, 0],
        }
        v39 = {
            "schema": "fold-protein-selected-states/v39",
            "sequence": sequence,
            "states": [1, 0],
            "parent_selected_states": v38["states"],
        }
        result = select_state_path_v40(sequence, v38, v39, parallel=False)
        self.assertEqual(result["lineage_seed_count"], 2)
        self.assertEqual(
            {row["seed"] for row in result["fixed_point_trace"]},
            {"v38_parent", "v39_causal_child"},
        )
        self.assertEqual(len(result["states"]), len(sequence))

    def test_collapsed_lineage_halts(self):
        sequence = "MA"
        v38 = {
            "schema": "fold-protein-selected-states/v38",
            "sequence": sequence,
            "states": [0, 0],
        }
        v39 = {
            "schema": "fold-protein-selected-states/v39",
            "sequence": sequence,
            "states": [0, 0],
            "parent_selected_states": v38["states"],
        }
        with self.assertRaises(RuntimeError):
            select_state_path_v40(sequence, v38, v39, parallel=False)


if __name__ == "__main__":
    unittest.main()
