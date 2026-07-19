import tempfile
from pathlib import Path
import unittest

import numpy as np

from verify.evaluate_sealed_blind_local_v3 import evaluate, kabsch_rmsd


ROOT = Path(__file__).resolve().parents[1]


class BlindLocalEvaluatorV3Tests(unittest.TestCase):
    def test_kabsch_removes_rigid_transform(self):
        source = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
        ])
        rotation = np.array([
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ])
        target = source @ rotation + np.array([7.0, -3.0, 2.0])
        self.assertAlmostEqual(kabsch_rmsd(source, target), 0.0, places=12)

    def test_reproduces_published_l8_post_seal_window(self):
        with tempfile.TemporaryDirectory() as held:
            result = evaluate(
                ROOT / "verify/blind_selector_v3.json",
                ROOT / "verify/development_runs/ubiquitin_v3_l8_20260719",
                ROOT / "verify/1ubq.pdb",
                Path(held) / "local.json",
                3,
            )
        self.assertEqual(result["window_count"], 6)
        best = result["minimum_kabsch_rmsd_window"]
        self.assertEqual(best["sequence"], "IFV")
        self.assertEqual(best["residue_positions_one_based"], [3, 5])
        self.assertAlmostEqual(best["local_tm_score"],
                               0.8821336259025588, places=12)
        self.assertAlmostEqual(best["kabsch_ca_rmsd_angstrom"],
                               0.18289611895543148, places=12)
        self.assertAlmostEqual(best["ca_drmsd_angstrom"],
                               0.16113130015884972, places=12)


if __name__ == "__main__":
    unittest.main()
