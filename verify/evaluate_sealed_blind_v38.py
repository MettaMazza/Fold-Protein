#!/usr/bin/env python3
"""Verify the V38 fixed-point seal before opening a comparison target."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculate_tm import compute_tm, parse_ca  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_v38_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path, sealed_dir = manifest_path.resolve(), sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v38":
        raise RuntimeError("invalid V38 manifest; target access forbidden")
    seal_path = sealed_dir / "seal.json"
    if not seal_path.is_file():
        raise RuntimeError("missing V38 seal; target access forbidden")
    seal = json.loads(seal_path.read_text())
    if (seal.get("schema") != "fold-protein-blind-seal/v38"
            or seal.get("status") != "completed"):
        raise RuntimeError("invalid V38 seal; target access forbidden")
    required = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "selected_states_sha256": sha256(sealed_dir / "selected_states.json"),
        "prediction_pdb_sha256": sha256(sealed_dir / "prediction.pdb"),
    }
    for field, actual in required.items():
        if seal.get(field) != actual:
            raise RuntimeError(f"V38 seal mismatch: {field}; target access forbidden")
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = json.loads((sealed_dir / "selector_input.json").read_text())["sequence"].upper()
    traces = states.get("descent_trace", [])
    coverage = {
        (row["direction"], tuple(row["axis_order"])) for row in traces
    }
    expected_coverage = {
        (direction, order)
        for direction in ("n_to_c", "c_to_n")
        for order in ((0, 1), (1, 0))
    }
    expected_evaluations = sum(
        len(row["sweeps"]) * (len(sequence) - 1) * 2 * 24
        for row in traces
    )
    if (states.get("sequence") != sequence
            or len(states.get("states", [])) != len(sequence)
            or len(states.get("parent_states", [])) != len(sequence)
            or states.get("axis_value_count") != 24
            or states.get("paired_state_count") != 576
            or states.get("descent_order_count") != 4
            or states.get("parallel_workers") != 4
            or coverage != expected_coverage
            or any(row["sweeps"][-1]["changed_coordinates"] != 0 for row in traces)
            or states.get("total_coordinate_evaluations") != expected_evaluations):
        raise RuntimeError("V38 complete fixed-point identity mismatch")
    if any(not 0 <= state < 576 for state in states["states"]):
        raise RuntimeError("V38 emitted a state outside the complete paired lattice")
    for relative, expected in manifest["source_sha256"].items():
        if seal["source_sha256"].get(relative) != expected or sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V38 source drift: {relative}; target access forbidden")
    return seal, states


def evaluate_v38(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    seal, states = verify_v38_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    prediction = parse_ca(str(sealed_dir.resolve() / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    prediction, target = prediction[:matched], target[:matched]
    pred_dist = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    evidence = {
        "schema": "fold-protein-blind-evaluation/v38",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "run_id": seal["run_id"],
        "execution": "post-seal structural comparison",
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "matched_ca_atoms": matched,
        "sequence_length": len(states["sequence"]),
        "tm_score": float(compute_tm(prediction, target)),
        "ca_drmsd_angstrom": float(np.sqrt(np.mean((pred_dist - target_dist) ** 2))),
        "states_changed_from_v37": sum(
            left != right for left, right in zip(states["states"], states["parent_states"])),
        "selected_descent": states["selected_descent"],
        "total_coordinate_evaluations": states["total_coordinate_evaluations"],
        "descent_sweeps": [
            {
                "direction": row["direction"],
                "axis_order": row["axis_order"],
                "sweeps": len(row["sweeps"]),
            }
            for row in states["descent_trace"]
        ],
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
    print(json.dumps(evaluate_v38(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
