import unittest

from tools.blind_24_lattice_selector_v23_1 import select_state_path_v23_1


class BlindSelectorV231Tests(unittest.TestCase):
    def test_parent_continuity_is_weight_free_and_not_a_lock(self):
        seed = [0] * 6
        result = select_state_path_v23_1("MQIFVK", seed)
        self.assertEqual(len(result["domain_trace"]), 5)
        self.assertTrue(all("parent_state_retained" in row
                            for row in result["domain_trace"]))
        self.assertEqual(
            result["parent_departures"],
            sum(left != right for left, right in zip(result["states"], seed)))
        self.assertEqual(result["final_relations"]["objectives"][-1],
                         result["parent_departures"])


if __name__ == "__main__":
    unittest.main()
