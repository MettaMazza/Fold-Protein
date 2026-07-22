#!/usr/bin/env python3
"""Verify the V45 seal, then compare every retained fixed point."""
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


def verify_v45_seal(manifest_path: Path, sealed_dir: Path):
    manifest_path = manifest_path.resolve()
    sealed_dir = sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    seal = json.loads((sealed_dir / "seal.json").read_text())
    if (manifest.get("schema") != "fold-protein-blind-selector/v45"
            or seal.get("schema") != "fold-protein-blind-seal/v45"):
        raise RuntimeError("invalid V45 seal")
    checks = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "frontier_sha256": sha256(sealed_dir / "frontier.json"),
    }
    for key, value in checks.items():
        if seal.get(key) != value:
            raise RuntimeError(f"V45 seal mismatch: {key}")
    for name, expected in seal["prediction_pdb_sha256"].items():
        if sha256(sealed_dir / name) != expected:
            raise RuntimeError(f"V45 PDB drift: {name}")
    for relative, expected in manifest["source_sha256"].items():
        if (sha256(ROOT / relative) != expected
                or seal["source_sha256"].get(relative) != expected):
            raise RuntimeError(f"V45 source drift: {relative}")
    frontier = json.loads((sealed_dir / "frontier.json").read_text())
    rows = frontier.get("frontier", [])
    traces = frontier.get("fixed_point_trace", [])
    if (frontier.get("connected_parent_count") != 3
            or frontier.get("axis_value_count") != 24
            or frontier.get("descent_order_count") != 4
            or frontier.get("fixed_point_trace_count") != 12
            or frontier.get("cycle_rank_target") != 1
            or len(traces) != 12
            or not rows
            or len(rows) != frontier.get("distinct_fixed_points")
            or any(row["graph_components"] != 1 for row in rows)
            or any(not row["sweeps"]
                   or row["sweeps"][-1]["changed_coordinates"] != 0
                   for row in traces)):
        raise RuntimeError("V45 complete fixed-point frontier drifted")
    coverage = {
        (row["seed"], row["direction"], tuple(row["axis_order"]))
        for row in traces
    }
    if len(coverage) != 12:
        raise RuntimeError("V45 boundary-axis coverage collapsed")
    return seal, frontier


def evaluate_v45(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    sealed_dir = sealed_dir.resolve()
    target_path = target_path.resolve()
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    _, frontier = verify_v45_seal(manifest_path, sealed_dir)
    # Target access begins only after the complete source-bound frontier, seal
    # and every emitted structure have been verified.
    target = parse_ca(str(target_path))
    rows = []
    for index, row in enumerate(frontier["frontier"]):
        prediction = parse_ca(str(sealed_dir / row["prediction_pdb"]))
        matched = min(len(prediction), len(target))
        pred, ref = prediction[:matched], target[:matched]
        pred_dist = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
        ref_dist = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=2)
        rows.append({
            "fixed_point_index": index,
            "source_orders": row["source_orders"],
            "cycle_distance_to_one": row["cycle_distance_to_one"],
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
        "schema": "fold-protein-blind-evaluation/v45",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "execution": "post-seal comparison of complete connected boundary-axis fixed-point frontier",
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
    print(json.dumps(evaluate_v45(
        args.manifest, args.sealed_dir, args.target, args.output
    ), sort_keys=True))


if __name__ == "__main__":
    main()
