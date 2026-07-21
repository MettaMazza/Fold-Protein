import unittest

from tools.blind_24_lattice_selector_v38 import (
    AXIS_ORDERS,
    AXIS_VALUE_COUNT,
    DESCENT_ORDERS,
    PAIRED_STATE_COUNT,
    _replace_coordinate,
)


class BlindSelectorV38Tests(unittest.TestCase):
    def test_complete_coordinate_and_order_grammar(self):
        self.assertEqual(AXIS_VALUE_COUNT, 24)
        self.assertEqual(PAIRED_STATE_COUNT, 576)
        self.assertEqual(set(AXIS_ORDERS), {(0, 1), (1, 0)})
        self.assertEqual(len(DESCENT_ORDERS), 4)

    def test_each_coordinate_scan_preserves_the_other_axis(self):
        state = 201
        phi_changed = [_replace_coordinate(state, 0, value) for value in range(24)]
        psi_changed = [_replace_coordinate(state, 1, value) for value in range(24)]
        self.assertEqual(len(set(phi_changed)), 24)
        self.assertEqual(len(set(psi_changed)), 24)
        self.assertTrue(all(candidate % 24 == state % 24 for candidate in phi_changed))
        self.assertTrue(all(candidate // 24 == state // 24 for candidate in psi_changed))

    def test_invalid_axis_halts(self):
        with self.assertRaises(ValueError):
            _replace_coordinate(201, 2, 0)


if __name__ == "__main__":
    unittest.main()
