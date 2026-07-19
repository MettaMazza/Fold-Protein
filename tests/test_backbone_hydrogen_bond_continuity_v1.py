import unittest

from tools.backbone_hydrogen_bond_continuity_v1 import (
    HYDROGEN_BOND_CONTINUITY_CENSUS, continuity_from_pairs,
    verify_hydrogen_bond_continuity_constitution)


class HydrogenBondContinuityTests(unittest.TestCase):
    def test_constitution_closes_to_successor_and_two_topologies(self):
        census = verify_hydrogen_bond_continuity_constitution()
        self.assertEqual(census, HYDROGEN_BOND_CONTINUITY_CENSUS)
        self.assertEqual(census["successor_distance"], 1)
        self.assertEqual(census["topology_classes"], ["alpha", "interstrand"])
        self.assertIsNone(census["continuity_weight"])

    def test_alpha_continuity_requires_same_direction_successors(self):
        result = continuity_from_pairs([
            {"topology": "alpha", "donor_residue": 5,
             "acceptor_residue": 1},
            {"topology": "alpha", "donor_residue": 6,
             "acceptor_residue": 2},
            {"topology": "alpha", "donor_residue": 8,
             "acceptor_residue": 4},
        ])
        self.assertEqual(result["continuity_counts"]["alpha"], 1)
        self.assertEqual(result["relations"]["alpha"], -1)

    def test_interstrand_continuity_admits_both_orientations(self):
        result = continuity_from_pairs([
            {"topology": "interstrand", "donor_residue": 10,
             "acceptor_residue": 30},
            {"topology": "interstrand", "donor_residue": 11,
             "acceptor_residue": 31},
            {"topology": "interstrand", "donor_residue": 20,
             "acceptor_residue": 40},
            {"topology": "interstrand", "donor_residue": 21,
             "acceptor_residue": 39},
        ])
        self.assertEqual(result["continuity_counts"]["interstrand"], 2)
        self.assertEqual(
            {edge["orientation"] for edge in result["edges"]},
            {"parallel", "antiparallel"})

    def test_unconnected_pairs_do_not_create_continuity(self):
        result = continuity_from_pairs([
            {"topology": "interstrand", "donor_residue": 10,
             "acceptor_residue": 30},
            {"topology": "interstrand", "donor_residue": 12,
             "acceptor_residue": 31},
        ])
        self.assertEqual(result["continuity_edge_count"], 0)


if __name__ == "__main__":
    unittest.main()
