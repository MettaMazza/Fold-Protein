#!/usr/bin/env python3
"""Verify the V43 seal, then compare every One-cycle frontier structure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from calculate_tm import compute_tm, parse_ca


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_v43_seal(manifest_path: Path, sealed_dir: Path):
    manifest_path = manifest_path.resolve()
    sealed_dir = sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    seal = json.loads((sealed_dir / "seal.json").read_text())
    if (manifest.get("schema") != "fold-protein-blind-selector/v43"
            or seal.get("schema") != "fold-protein-blind-seal/v43"):
        raise RuntimeError("invalid V43 seal")
    checks = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "frontier_sha256": sha256(sealed_dir / "frontier.json"),
    }
    for key, value in checks.items():
        if seal.get(key) != value:
            raise RuntimeError(f"V43 seal mismatch: {key}")
    for name, expected in seal["prediction_pdb_sha256"].items():
        if sha256(sealed_dir / name) != expected:
            raise RuntimeError(f"V43 PDB drift: {name}")
    for relative, expected in manifest["source_sha256"].items():
        if (sha256(ROOT / relative) != expected
                or seal["source_sha256"].get(relative) != expected):
            raise RuntimeError(f"V43 source drift: {relative}")
    frontier = json.loads((sealed_dir / "frontier.json").read_text())
    rows = frontier.get("frontier", [])
    if (frontier.get("component_cube_candidates") != 8192
            or frontier.get("cycle_rank_target") != 1
            or frontier.get("one_cycle_frontier_count") != 1082
            or len(rows) != 1082
            or any(row["graph_cycle_rank"] != 1 for row in rows)):
        raise RuntimeError("V43 complete One-cycle frontier drifted")
    return seal, frontier


def evaluate_v43(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    sealed_dir = sealed_dir.resolve()
    target_path = target_path.resolve()
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    seal, frontier = verify_v43_seal(manifest_path, sealed_dir)
    # Target access begins only after source, seal, complete frontier and all
    # 1,082 emitted structures have been verified.
    target = parse_ca(str(target_path))
    rows = []
    for row in frontier["frontier"]:
        prediction = parse_ca(str(sealed_dir / row["prediction_pdb"]))
        matched = min(len(prediction), len(target))
        pred, ref = prediction[:matched], target[:matched]
        pred_dist = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
        ref_dist = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=2)
        rows.append({
            "mask": row["mask"],
            "graph_cycle_rank": row["graph_cycle_rank"],
            "graph_components": row["graph_components"],
            "interblock_edges": row["interblock_edges"],
            "contact_residue_pairs": row["contact_residue_pairs"],
            "contact_atom_pairs": row["contact_atom_pairs"],
            "prediction_pdb_sha256": row["prediction_pdb_sha256"],
            "matched_ca_atoms": matched,
            "tm_score": float(compute_tm(pred, ref)),
            "ca_drmsd_angstrom": float(
                np.sqrt(np.mean((pred_dist - ref_dist) ** 2))
            ),
        })
    evidence = {
        "schema": "fold-protein-blind-evaluation/v43",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "execution": "post-seal comparison of complete One-cycle frontier",
        "run_id": frontier["run_id"],
        "seal_sha256": sha256(sealed_dir / "seal.json"),
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
    print(json.dumps(evaluate_v43(
        args.manifest, args.sealed_dir, args.target, args.output
    ), sort_keys=True))


if __name__ == "__main__":
    main()
