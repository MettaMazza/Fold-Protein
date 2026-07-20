import unittest

from tools.blind_24_lattice_selector_v23_2 import select_state_path_v23_2


class BlindSelectorV232Tests(unittest.TestCase):
    def test_all_states_are_locally_admitted_before_global_assembly(self):
        result = select_state_path_v23_2("MQIFVK", [0] * 6)
        self.assertTrue(all(row["expanded_state_count"] == 576
                            for row in result["domain_trace"]))
        self.assertTrue(all(row["locally_admitted_state_count"] == 24
                            for row in result["domain_trace"]))
        self.assertEqual({row["direction"] for row in result["assembly_trace"]},
                         {"forward", "reverse"})


if __name__ == "__main__":
    unittest.main()
