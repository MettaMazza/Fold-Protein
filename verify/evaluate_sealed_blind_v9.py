#!/usr/bin/env python3
"""Verify selector-v9 sealing before opening a comparison target."""
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


def verify_v9_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path = manifest_path.resolve()
    sealed_dir = sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v9":
        raise RuntimeError("invalid v9 manifest; target access forbidden")
    seal_path = sealed_dir / "seal.json"
    if not seal_path.is_file():
        raise RuntimeError("missing v9 seal; target access forbidden")
    seal = json.loads(seal_path.read_text())
    if seal.get("schema") != "fold-protein-blind-seal/v9" or \
            seal.get("status") != "completed":
        raise RuntimeError("invalid or incomplete v9 seal; target access forbidden")
    required = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "selected_states_sha256": sha256(sealed_dir / "selected_states.json"),
        "prediction_pdb_sha256": sha256(sealed_dir / "prediction.pdb"),
    }
    for field, actual in required.items():
        if seal.get(field) != actual:
            raise RuntimeError(f"v9 seal mismatch for {field}; target access forbidden")
    selector_input = json.loads((sealed_dir / "selector_input.json").read_text())
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = selector_input.get("sequence", "").upper()
    if states.get("sequence") != sequence or \
            states.get("run_id") != selector_input.get("run_id"):
        raise RuntimeError("v9 input/state identity mismatch; target access forbidden")
    if hashlib.sha256(sequence.encode()).hexdigest() != seal.get("sequence_sha256"):
        raise RuntimeError("v9 sequence hash mismatch; target access forbidden")
    if len(states.get("states", [])) != seal.get("path_length") or \
            seal.get("path_length") != len(sequence):
        raise RuntimeError("v9 path length mismatch; target access forbidden")
    expected_quartets = max(0, len(sequence) - 3)
    if len(states.get("orientation_trace", [])) != expected_quartets or \
            seal.get("orientation_quartets") != expected_quartets:
        raise RuntimeError("v9 orientation trace mismatch; target access forbidden")
    if states.get("orientation_modes") != seal.get("generated_orientation_modes"):
        raise RuntimeError("v9 generated-mode mismatch; target access forbidden")
    if states.get("charge_census") != seal.get("charge_census") or \
            states.get("steric_census") != seal.get("steric_census"):
        raise RuntimeError("v9 residue constitution mismatch; target access forbidden")
    if states.get("mode_capacity") != seal.get("mode_capacity") or \
            seal.get("binary_mode_count") * seal.get("mode_capacity") != 24:
        raise RuntimeError("v9 mode-capacity mismatch; target access forbidden")
    for row in states.get("mode_balance_trace", []):
        if set(row) != {"alpha", "beta"}:
            raise RuntimeError("v9 mode balance is incomplete; target access forbidden")
    for relative, expected in seal.get("source_sha256", {}).items():
        if manifest.get("source_sha256", {}).get(relative) != expected or \
                sha256(ROOT / relative) != expected:
            raise RuntimeError(f"v9 source mismatch for {relative}; target access forbidden")
    return seal, states


def evaluate_v9(manifest_path: Path, sealed_dir: Path, target_path: Path,
                output_path: Path) -> dict:
    seal, states = verify_v9_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    prediction = parse_ca(str(sealed_dir.resolve() / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    if matched < 1:
        raise RuntimeError("no matched C-alpha coordinates")
    prediction = prediction[:matched]
    target = target[:matched]
    pred_dist = np.linalg.norm(
        prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(
        target[:, None, :] - target[None, :, :], axis=2)
    evidence = {
        "schema": "fold-protein-blind-evaluation/v9",
        "status": "completed",
        "run_id": seal["run_id"],
        "execution": "post-seal structural comparison",
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "matched_ca_atoms": matched,
        "tm_score": float(compute_tm(prediction, target)),
        "ca_drmsd_angstrom": float(
            np.sqrt(np.mean((pred_dist - target_dist) ** 2))),
        "sequence_length": len(states["sequence"]),
    }
    output_path.resolve().write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_v9(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
