import unittest

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from tools.sidechain_spatial_exclusion_v1 import (
    sidechain_spatial_exclusion_relation as v1_relation)
from tools.sidechain_spatial_exclusion_v2 import (
    SIDECHAIN_SPATIAL_EXCLUSION_CENSUS,
    sidechain_spatial_exclusion_relation as v2_relation)


class BinarySidechainSpatialExclusionTests(unittest.TestCase):
    def test_pair_existence_is_hard_and_encounter_product_is_retained(self):
        sequence = "MQIFVKTL"
        states = [11, 201, 21, 309, 17, 205, 33, 1]
        phi = [angles_for_state(state)[0] for state in states]
        psi = [angles_for_state(state)[1] for state in states]
        atoms = build_backbone_coordinates(sequence, phi, psi)
        old = v1_relation(sequence, atoms)
        new = v2_relation(sequence, atoms)
        self.assertEqual(
            new["hard_exclusions"], new["excluded_residue_pair_count"])
        self.assertEqual(
            new["possible_heavy_atom_encounters"],
            old["possible_heavy_atom_encounters"])
        self.assertEqual(new["excluded_pairs"], old["excluded_pairs"])

    def test_census_forbids_encounter_multiplicity_in_hard_stratum(self):
        self.assertIn("not a multiplier", SIDECHAIN_SPATIAL_EXCLUSION_CENSUS[
            "encounter_census_role"])


if __name__ == "__main__":
    unittest.main()
