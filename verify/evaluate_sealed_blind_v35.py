#!/usr/bin/env python3
"""Verify the V35 seal before opening a comparison target."""
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


def verify_v35_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path, sealed_dir = manifest_path.resolve(), sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v35":
        raise RuntimeError("invalid V35 manifest; target access forbidden")
    seal_path = sealed_dir / "seal.json"
    if not seal_path.is_file():
        raise RuntimeError("missing V35 seal; target access forbidden")
    seal = json.loads(seal_path.read_text())
    if (seal.get("schema") != "fold-protein-blind-seal/v35"
            or seal.get("status") != "completed"):
        raise RuntimeError("invalid V35 seal; target access forbidden")
    required = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "selected_states_sha256": sha256(sealed_dir / "selected_states.json"),
        "prediction_pdb_sha256": sha256(sealed_dir / "prediction.pdb"),
    }
    for field, actual in required.items():
        if seal.get(field) != actual:
            raise RuntimeError(f"V35 seal mismatch: {field}; target access forbidden")
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = json.loads((sealed_dir / "selector_input.json").read_text())["sequence"].upper()
    if (states.get("sequence") != sequence
            or len(states.get("states", [])) != len(sequence)
            or states.get("boundary_contexts") != 8
            or states.get("quartet_transitions") != 16):
        raise RuntimeError("V35 boundary state identity mismatch")
    domain = set(states["closed_domain"].values())
    if any(state not in domain for state in states["states"][:-1]):
        raise RuntimeError("V35 emitted a state outside the engine-closed domain")
    for row in states["boundary_trace"][3:]:
        if (row["expanded_transitions"] != 16
                or row["retained_contexts"] != 8
                or row["inbound_per_context"] != [2]):
            raise RuntimeError("V35 complete boundary propagation drifted")
    for relative, expected in manifest["source_sha256"].items():
        if seal["source_sha256"].get(relative) != expected or sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V35 source drift: {relative}; target access forbidden")
    return seal, states


def evaluate_v35(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    seal, states = verify_v35_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    prediction = parse_ca(str(sealed_dir.resolve() / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    prediction, target = prediction[:matched], target[:matched]
    pred_dist = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    evidence = {
        "schema": "fold-protein-blind-evaluation/v35",
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
        "mode_census": {
            mode: states["modes"].count(mode)
            for mode in sorted(set(states["modes"]))
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
    print(json.dumps(evaluate_v35(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
