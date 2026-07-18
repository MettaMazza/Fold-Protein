import json
import math
from pathlib import Path
import tempfile
import unittest

from tools.predict_structure import build_backbone_coordinates as legacy_build
from tools.protein_backbone_geometry_v1 import (
    build_backbone_coordinates,
    write_pdb,
)
from verify.replay_protein_backbone_geometry_v1 import replay


ROOT = Path(__file__).resolve().parents[1]


class ProteinBackboneGeometryV1Tests(unittest.TestCase):
    def test_exact_coordinate_rederivation(self):
        sequence = "MQIFVKTL"
        states = [19, 31, 408, 18, 189, 115, 168, 0]
        phi = [math.radians(-180 + 15 * (state // 24)) for state in states]
        psi = [math.radians(-180 + 15 * (state % 24)) for state in states]
        old = legacy_build(sequence, ["C"] * len(sequence), phi, psi)
        new = build_backbone_coordinates(sequence, phi, psi)
        self.assertEqual(old, new)

    def test_protected_witness_replays_byte_exactly(self):
        receipt = replay()
        manifest = json.loads(
            (ROOT / "verify/ubiquitin_24_lattice_manifest.json").read_text()
        )
        self.assertEqual(
            receipt["constructed_pdb_sha256"],
            manifest["sha256"]["constructed_pdb"],
        )

    def test_module_emits_historical_pdb_bytes(self):
        sequence = "MQ"
        phi = [math.radians(-180), math.radians(-165)]
        psi = [math.radians(-180), math.radians(-165)]
        old = legacy_build(sequence, ["C", "C"], phi, psi)
        new = build_backbone_coordinates(sequence, phi, psi)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "new.pdb"
            write_pdb(new, path)
            self.assertTrue(path.read_text().endswith("END\n"))
        self.assertEqual(old, new)


if __name__ == "__main__":
    unittest.main()
