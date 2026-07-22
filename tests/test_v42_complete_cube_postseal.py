import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V42CompleteCubePostsealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((RUN / "complete_cube_postseal.json").read_text())

    def test_every_precomparison_sealed_cube_path_is_measured(self):
        rows = self.evidence["frontier"]
        self.assertEqual(self.evidence["candidate_count"], 8192)
        self.assertEqual([row["mask"] for row in rows], list(range(8192)))
        self.assertEqual(len({row["states_sha256"] for row in rows}), 8192)

    def test_evidence_remains_bound_to_sources_and_seal(self):
        self.assertEqual(
            self.evidence["evaluator_sha256"],
            sha256(ROOT / "verify/evaluate_v42_complete_cube_postseal.py"),
        )
        self.assertEqual(self.evidence["seal_sha256"], sha256(RUN / "seal.json"))
        self.assertEqual(
            self.evidence["sealed_frontier_sha256"], sha256(RUN / "frontier.json")
        )
        self.assertEqual(
            self.evidence["target_sha256"], sha256(ROOT / "verify/1ubq.pdb")
        )

    def test_positive_extrema_are_preserved_without_selector_promotion(self):
        rows = self.evidence["frontier"]
        maximum_tm = max(rows, key=lambda row: row["tm_score"])
        minimum_drmsd = min(rows, key=lambda row: row["ca_drmsd_angstrom"])
        self.assertEqual(maximum_tm["mask"], 525)
        self.assertAlmostEqual(maximum_tm["tm_score"], 0.1797422881025564)
        self.assertAlmostEqual(maximum_tm["ca_drmsd_angstrom"], 6.001711929850275)
        self.assertEqual(minimum_drmsd["mask"], 653)
        self.assertAlmostEqual(minimum_drmsd["tm_score"], 0.14743848289356878)
        self.assertAlmostEqual(minimum_drmsd["ca_drmsd_angstrom"], 5.513018735394969)
        dual = [
            row for row in rows
            if row["tm_score"] > 0.15437792615180457
            and row["ca_drmsd_angstrom"] < 6.1032086928107425
        ]
        self.assertEqual(len(dual), 13)


if __name__ == "__main__":
    unittest.main()
