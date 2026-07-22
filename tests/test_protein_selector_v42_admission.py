import unittest
from tools.verify_protein_selector_v42_admission import verify_selector_v42_admission
class ProteinSelectorV42AdmissionTests(unittest.TestCase):
    def test_complete_connected_frontier_is_admitted(self):
        row=verify_selector_v42_admission();self.assertEqual(row["status"],"verified");self.assertEqual(row["masks"],[2178,5814,5815])
if __name__=="__main__": unittest.main()
