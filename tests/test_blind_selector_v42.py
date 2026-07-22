import unittest

from tools.blind_24_lattice_selector_v42 import (
    graph_component_count, maximal_status_blocks)


class BlindSelectorV42Tests(unittest.TestCase):
    def test_status_blocks_are_unique_maximal_partition(self):
        blocks = maximal_status_blocks((1, 1, 2, 3, 3), (0, 0, 2, 4, 3))
        self.assertEqual(blocks, (
            (True, (0, 1)), (False, (2,)), (True, (3,)), (False, (4,))))

    def test_graph_component_count_reaches_one(self):
        self.assertEqual(graph_component_count(4, {(0, 1), (1, 2), (2, 3)}), 1)
        self.assertEqual(graph_component_count(4, {(0, 1), (2, 3)}), 2)


if __name__ == "__main__":
    unittest.main()
