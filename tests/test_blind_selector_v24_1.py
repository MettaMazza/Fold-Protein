import unittest
from tools.blind_24_lattice_selector_v24_1 import select_state_path_v24_1

class BlindSelectorV241Tests(unittest.TestCase):
    def test_segment_boundaries_and_complete_local_windows_are_closed(self):
        sequence="MQIFVK";domains=[{"residue":i+1,"expanded_state_count":576,"retained_states":list(range(24))} for i in range(len(sequence)-1)]
        result=select_state_path_v24_1(sequence,[0]*len(sequence),domains)
        self.assertTrue(all(row["boundary_active_states"] for row in result["assembly_trace"]))
        self.assertEqual(result["reconciliation"]["complete_local_window_count"],len(sequence)-1)

if __name__=="__main__":unittest.main()
