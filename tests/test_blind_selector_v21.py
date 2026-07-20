import unittest
from pathlib import Path

from tools.blind_24_lattice_selector_v13 import generated_local_relations_v13
from tools.blind_24_lattice_selector_v21 import (
    CONSTITUTIONAL_OBJECTIVES, generated_prefix_relations_v21)
from tools.sidechain_graph_contact_topology_v1 import (
    CONTACT_SHELL, sidechain_graph_contact_relation)
from tools.blind_24_lattice_selector_v3 import build_lookahead_prefix


ROOT = Path(__file__).resolve().parents[1]


class BlindSelectorV21Tests(unittest.TestCase):
    def test_contact_shell_is_exact_and_target_incapable(self):
        self.assertEqual(CONTACT_SHELL["inner_boundary"][:3], "1/2")
        self.assertEqual(CONTACT_SHELL["outer_boundary"][:3], "one")
        for key in ("empirical_radius", "empirical_cutoff", "fitted_weight",
                    "reward", "target"):
            self.assertIsNone(CONTACT_SHELL[key])

    def test_contact_count_is_appended_as_one_global_objective(self):
        sequence = "MQIFVK"
        path = [0, 1, 2, 3, 4]
        atoms = build_lookahead_prefix(sequence, path)
        contact = sidechain_graph_contact_relation(sequence, atoms)
        relation = generated_prefix_relations_v21(sequence, path)
        self.assertEqual(CONSTITUTIONAL_OBJECTIVES, 16)
        self.assertEqual(relation[-1], -contact["atom_contact_count"])

    def test_local_route_remains_exact_v13(self):
        sequence = "MQIFVK"
        path = [0, 1, 2, 3, 4]
        from tools.blind_24_lattice_selector_v19 import generated_local_relations_v19
        local = generated_local_relations_v19(sequence, path)
        v13 = generated_local_relations_v13(sequence, path)
        self.assertEqual(local, (v13[0], (v13[1], 0), *v13[2:]))

    def test_import_closure_is_target_incapable(self):
        for relative in (
                "tools/blind_24_lattice_selector_v21.py",
                "tools/sidechain_graph_contact_topology_v1.py"):
            source = (ROOT / relative).read_text().lower()
            self.assertNotIn("1ubq", source)
            self.assertNotIn("calculate_tm", source)
            self.assertNotIn("biopython", source)


if __name__ == "__main__":
    unittest.main()
