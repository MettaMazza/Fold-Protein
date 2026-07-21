import unittest

from tools.blind_24_lattice_selector_v41 import (
    component_cube_candidate,
    maximal_disagreement_components,
)


class BlindSelectorV41Tests(unittest.TestCase):
    def test_maximal_components_are_unique_and_complete(self):
        left = (0, 0, 0, 0, 0, 0, 0)
        right = (1, 1, 0, 1, 0, 1, 1)
        components = maximal_disagreement_components(left, right)
        self.assertEqual(components, ((0, 1), (3,), (5, 6)))
        self.assertEqual(sum(map(len, components)), 5)

    def test_complete_component_cube_contains_both_parents(self):
        left = (0, 0, 0, 0, 0, 0, 0)
        right = (1, 1, 0, 1, 0, 1, 1)
        components = maximal_disagreement_components(left, right)
        candidates = {
            component_cube_candidate(left, right, components, mask)
            for mask in range(1 << len(components))
        }
        self.assertEqual(len(candidates), 8)
        self.assertIn(left, candidates)
        self.assertIn(right, candidates)

    def test_component_assignment_never_splits_a_component(self):
        left = (0, 0, 0, 0)
        right = (1, 1, 0, 1)
        components = maximal_disagreement_components(left, right)
        for mask in range(1 << len(components)):
            candidate = component_cube_candidate(left, right, components, mask)
            self.assertIn(candidate[:2], (left[:2], right[:2]))


if __name__ == "__main__":
    unittest.main()
