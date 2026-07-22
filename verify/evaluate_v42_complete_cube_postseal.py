#!/usr/bin/env python3
"""Measure every state path already bound inside the sealed V42 component cube."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from calculate_tm import compute_tm, parse_ca
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from verify.evaluate_sealed_blind_v42 import verify_v42_seal


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, separators=(",", ":")).encode()
    ).hexdigest()


def ca_coordinates(sequence: str, path: list[int]) -> np.ndarray:
    states = list(path) + [CANONICAL_STATE]
    if len(states) != len(sequence):
        raise RuntimeError("V42 cube path length drifted")
    atoms = build_backbone_coordinates(
        sequence,
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states],
    )
    # Match the repository evaluator's real executable path: PDB emission writes
    # each coordinate at three decimal places before `parse_ca` reads it back.
    return np.asarray([
        [float(f"{coordinate:.3f}") for coordinate in atom["coord"]]
        for atom in atoms if atom["name"] == "CA"
    ])


def evaluate(manifest_path: Path, sealed_dir: Path, target_path: Path,
             output_path: Path) -> dict:
    manifest_path = manifest_path.resolve()
    sealed_dir = sealed_dir.resolve()
    target_path = target_path.resolve()
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)

    seal, frontier = verify_v42_seal(manifest_path, sealed_dir)
    trace = frontier["component_cube_trace"]
    if len(trace) != 8192 or [row["mask"] for row in trace] != list(range(8192)):
        raise RuntimeError("V42 sealed complete cube census drifted")
    # Candidate construction was completed and hash-sealed in frontier.json before
    # this evaluator opens the target. No target value can alter a state path.
    target = parse_ca(str(target_path))
    sequence = frontier["sequence"]
    rows = []
    for row in trace:
        prediction = ca_coordinates(sequence, row["path"])
        matched = min(len(prediction), len(target))
        pred, ref = prediction[:matched], target[:matched]
        pred_dist = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
        ref_dist = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=2)
        states = row["path"] + [CANONICAL_STATE]
        rows.append({
            "mask": row["mask"],
            "states_sha256": json_sha(states),
            "graph_components": row["graph_components"],
            "interblock_edges": row["interblock_edges"],
            "contact_residue_pairs": row["contact_residue_pairs"],
            "contact_atom_pairs": row["contact_atom_pairs"],
            "matched_ca_atoms": matched,
            "tm_score": float(compute_tm(pred, ref)),
            "ca_drmsd_angstrom": float(
                np.sqrt(np.mean((pred_dist - ref_dist) ** 2))
            ),
        })
    evidence = {
        "schema": "fold-protein-v42-complete-cube-postseal-evaluation/v1",
        "status": "completed",
        "result_type": "post-seal cumulative development complete-cube evaluation",
        "official_run": False,
        "execution": "post-seal comparison of all 8,192 already-sealed component assignments",
        "run_id": frontier["run_id"],
        "seal_sha256": sha256(sealed_dir / "seal.json"),
        "sealed_frontier_sha256": seal["frontier_sha256"],
        "evaluator_sha256": sha256(Path(__file__).resolve()),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "candidate_count": len(rows),
        "frontier": rows,
    }
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(
        args.manifest, args.sealed_dir, args.target, args.output
    ), sort_keys=True))


if __name__ == "__main__":
    main()
