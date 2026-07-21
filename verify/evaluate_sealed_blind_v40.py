#!/usr/bin/env python3
"""Verify the V40 lineage-paired seal before opening a comparison target."""
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


def verify_v40_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path, sealed_dir = manifest_path.resolve(), sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v40":
        raise RuntimeError("invalid V40 manifest; target access forbidden")
    seal_path = sealed_dir / "seal.json"
    if not seal_path.is_file():
        raise RuntimeError("missing V40 seal; target access forbidden")
    seal = json.loads(seal_path.read_text())
    if (seal.get("schema") != "fold-protein-blind-seal/v40"
            or seal.get("status") != "completed"):
        raise RuntimeError("invalid V40 seal; target access forbidden")
    required = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "selected_states_sha256": sha256(sealed_dir / "selected_states.json"),
        "prediction_pdb_sha256": sha256(sealed_dir / "prediction.pdb"),
    }
    for field, actual in required.items():
        if seal.get(field) != actual:
            raise RuntimeError(f"V40 seal mismatch: {field}; target access forbidden")
    if (seal.get("parent_v38") != manifest.get("parent_v38")
            or seal.get("parent_v39") != manifest.get("parent_v39")):
        raise RuntimeError("V40 lineage binding mismatch; target access forbidden")
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = json.loads((sealed_dir / "selector_input.json").read_text())["sequence"].upper()
    if (states.get("sequence") != sequence
            or len(states.get("states", [])) != len(sequence)
            or states.get("lineage_seed_count") != 2
            or states.get("paired_state_count") != 576
            or states.get("causal_direction") != "n_to_c"
            or len(states.get("fixed_point_trace", [])) != 2):
        raise RuntimeError("V40 complete lineage-paired identity mismatch")
    if any(not 0 <= state < 576 for state in states["states"]):
        raise RuntimeError("V40 emitted a state outside the complete paired lattice")
    for row in states["fixed_point_trace"]:
        if row["sweeps"][-1]["changed_states"] != 0:
            raise RuntimeError("V40 trace contains a non-fixed-point emission")
    for relative, expected in manifest["source_sha256"].items():
        if seal["source_sha256"].get(relative) != expected or sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V40 source drift: {relative}; target access forbidden")
    return seal, states


def evaluate_v40(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    seal, states = verify_v40_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    prediction = parse_ca(str(sealed_dir.resolve() / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    prediction, target = prediction[:matched], target[:matched]
    pred_dist = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    evidence = {
        "schema": "fold-protein-blind-evaluation/v40",
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
        "states_changed_from_v38": sum(
            left != right for left, right in zip(states["states"], states["parent_v38_states"])),
        "states_changed_from_v39": sum(
            left != right for left, right in zip(states["states"], states["parent_v39_states"])),
        "lineage_seed_count": states["lineage_seed_count"],
        "paired_state_count": states["paired_state_count"],
        "causal_direction": states["causal_direction"],
        "distinct_fixed_points": states["distinct_fixed_points"],
        "selected_fixed_point": states["selected_fixed_point"],
        "total_paired_evaluations": states["total_paired_evaluations"],
        "fixed_point_sweeps": {
            row["seed"]: len(row["sweeps"])
            for row in states["fixed_point_trace"]
        },
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
    print(json.dumps(evaluate_v40(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
