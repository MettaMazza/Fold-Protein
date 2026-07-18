import unittest

from tools.trace_selector_continuation_lineage_v2 import descendant_status


class SelectorContinuationLineageV2Tests(unittest.TestCase):
    def test_descendant_relation_counts_and_ranks_exact_prefixes(self):
        beam = [
            ((0, 1.0, 1.0), (1, 3, 8)),
            ((0, 1.0, 2.0), (1, 2, 7)),
            ((0, 1.0, 3.0), (1, 2, 9)),
        ]
        status = descendant_status(beam, (1, 2))
        self.assertEqual(status["retained_descendants"], 2)
        self.assertEqual(status["best_rank"], 2)
        self.assertTrue(status["lineage_alive"])

    def test_absent_prefix_is_extinct(self):
        status = descendant_status([((0, 1.0, 1.0), (2, 3))], (1,))
        self.assertEqual(status["retained_descendants"], 0)
        self.assertIsNone(status["best_rank"])
        self.assertFalse(status["lineage_alive"])


if __name__ == "__main__":
    unittest.main()
