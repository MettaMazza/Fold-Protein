#!/usr/bin/env python3
"""Verify a reconstructed target-free frontier seal, then measure every row."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from calculate_tm import compute_tm, parse_ca


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(frontier_dir: Path, target_path: Path, output_path: Path) -> dict:
    frontier_dir = frontier_dir.resolve()
    target_path = target_path.resolve()
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    seal = json.loads((frontier_dir / "seal.json").read_text())
    frontier = json.loads((frontier_dir / "frontier.json").read_text())
    if seal.get("status") != "completed" or frontier.get("status") != "completed":
        raise RuntimeError("reconstructed frontier is incomplete")
    if seal.get("frontier_sha256") != sha256(frontier_dir / "frontier.json"):
        raise RuntimeError("reconstructed frontier seal drifted")
    if seal.get("candidate_count") != len(frontier.get("candidates", [])):
        raise RuntimeError("reconstructed frontier census drifted")
    for name, expected in seal["prediction_pdb_sha256"].items():
        if sha256(frontier_dir / name) != expected:
            raise RuntimeError(f"reconstructed frontier PDB drifted: {name}")

    target = parse_ca(str(target_path))
    rows = []
    for row in frontier["candidates"]:
        prediction = parse_ca(str(frontier_dir / row["prediction_pdb"]))
        matched = min(len(prediction), len(target))
        pred, ref = prediction[:matched], target[:matched]
        pred_dist = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
        ref_dist = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=2)
        rows.append({
            "candidate_index": row["candidate_index"],
            "selected_emission": row["selected_emission"],
            "states_sha256": row["states_sha256"],
            "prediction_pdb": row["prediction_pdb"],
            "prediction_pdb_sha256": row["prediction_pdb_sha256"],
            "matched_ca_atoms": matched,
            "tm_score": float(compute_tm(pred, ref)),
            "ca_drmsd_angstrom": float(
                np.sqrt(np.mean((pred_dist - ref_dist) ** 2))
            ),
        })
    evidence = {
        "schema": "fold-protein-reconstructed-frontier-evaluation/v1",
        "status": "completed",
        "result_type": "post-seal cumulative development frontier recovery",
        "official_run": False,
        "execution": "post-seal comparison of complete reconstructed frontier",
        "run_id": frontier["run_id"],
        "frontier_seal_sha256": sha256(frontier_dir / "seal.json"),
        "frontier_sha256": seal["frontier_sha256"],
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "candidate_count": len(rows),
        "frontier": rows,
    }
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frontier_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.frontier_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
