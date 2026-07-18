#!/usr/bin/env python3
"""Replay the protected witness through the target-incapable geometry module."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile

from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay() -> dict:
    manifest_path = ROOT / "verify/ubiquitin_24_lattice_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    states = manifest["states"]
    sequence = manifest["sequence"]
    phi = [math.radians(-180 + 15 * (state // 24)) for state in states]
    psi = [math.radians(-180 + 15 * (state % 24)) for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    with tempfile.TemporaryDirectory(prefix="fold-protein-geometry-replay-") as tmp:
        candidate = Path(tmp) / "replayed.pdb"
        write_pdb(atoms, candidate)
        candidate_sha = sha256(candidate)
    expected = manifest["sha256"]["constructed_pdb"]
    if candidate_sha != expected:
        raise RuntimeError(
            f"target-incapable geometry replay mismatch: {candidate_sha} != {expected}"
        )
    return {
        "schema": "fold-protein-backbone-geometry-replay/v1",
        "status": "verified",
        "residues": len(sequence),
        "states": len(states),
        "constructed_pdb_sha256": candidate_sha,
        "manifest_sha256": sha256(manifest_path),
    }


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True))
