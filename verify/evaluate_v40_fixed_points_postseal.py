#!/usr/bin/env python3
"""Measure every already-sealed V40 lineage fixed point after seal verification."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import numpy as np

from calculate_tm import compute_tm, parse_ca
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb
from verify.evaluate_sealed_blind_v40 import verify_v40_seal


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ca_for_path(sequence: str, path: list[int]) -> np.ndarray:
    states = list(path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    # Match the registered prediction boundary exactly: coordinates are first
    # emitted through the repository PDB writer and then parsed for comparison.
    with tempfile.TemporaryDirectory(prefix="fold-protein-v40-postseal-") as directory:
        pdb_path = Path(directory) / "fixed-point.pdb"
        write_pdb(atoms, pdb_path)
        return parse_ca(str(pdb_path))


def evaluate_fixed_points(manifest_path: Path, sealed_dir: Path,
                          target_path: Path, output_path: Path) -> dict:
    seal, states = verify_v40_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    target = parse_ca(str(target_path))
    rows = []
    for trace in states["fixed_point_trace"]:
        prediction = _ca_for_path(states["sequence"], trace["path"])
        matched = min(len(prediction), len(target))
        pred, ref = prediction[:matched], target[:matched]
        pred_dist = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
        ref_dist = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=2)
        rows.append({
            "seed": trace["seed"],
            "selected_emission": trace["seed"] == states["selected_fixed_point"],
            "sweeps": len(trace["sweeps"]),
            "evaluations": trace["evaluations"],
            "tm_score": float(compute_tm(pred, ref)),
            "ca_drmsd_angstrom": float(np.sqrt(np.mean((pred_dist - ref_dist) ** 2))),
        })
    evidence = {
        "schema": "fold-protein-v40-fixed-point-postseal-evaluation/v1",
        "status": "completed",
        "result_type": "post-seal cumulative development diagnostic",
        "official_run": False,
        "run_id": seal["run_id"],
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "selected_states_sha256": seal["selected_states_sha256"],
        "evaluator_sha256": sha256(Path(__file__).resolve()),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "fixed_points": rows,
    }
    if output_path.exists():
        raise FileExistsError(output_path)
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_fixed_points(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
