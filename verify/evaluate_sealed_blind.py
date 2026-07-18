#!/usr/bin/env python3
"""Verify a blind seal completely before opening the comparison target."""
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


def verify_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest = json.loads(manifest_path.read_text())
    seal_path = sealed_dir / "seal.json"
    if not seal_path.is_file():
        raise RuntimeError("missing seal; target access forbidden")
    seal = json.loads(seal_path.read_text())
    if seal.get("schema") != "fold-protein-blind-seal/v1" or seal.get("status") != "completed":
        raise RuntimeError("invalid or incomplete seal; target access forbidden")
    checks = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "selected_states_sha256": sha256(sealed_dir / "selected_states.json"),
        "prediction_pdb_sha256": sha256(sealed_dir / "prediction.pdb"),
    }
    for field, actual in checks.items():
        if seal.get(field) != actual:
            raise RuntimeError(f"seal mismatch for {field}; target access forbidden")
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = states.get("sequence", "")
    if hashlib.sha256(sequence.encode()).hexdigest() != seal.get("sequence_sha256"):
        raise RuntimeError("sealed sequence mismatch; target access forbidden")
    if len(states.get("states", [])) != seal.get("path_length"):
        raise RuntimeError("sealed path-length mismatch; target access forbidden")
    for relative, expected in seal.get("source_sha256", {}).items():
        if manifest["source_sha256"].get(relative) != expected or sha256(ROOT / relative) != expected:
            raise RuntimeError(f"sealed source mismatch for {relative}; target access forbidden")
    return seal, states


def evaluate(manifest_path: Path, sealed_dir: Path, target_path: Path,
             output_path: Path) -> dict:
    seal, states = verify_seal(manifest_path.resolve(), sealed_dir.resolve())

    # The target is not opened or hashed until every prediction-side check above passes.
    target_path = target_path.resolve()
    target_hash = sha256(target_path)
    prediction = parse_ca(str(sealed_dir / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    if matched < 1:
        raise RuntimeError("no matched Cα coordinates")
    prediction = prediction[:matched]
    target = target[:matched]
    tm_score = float(compute_tm(prediction, target))
    pred_dist = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    drmsd = float(np.sqrt(np.mean((pred_dist - target_dist) ** 2)))
    evidence = {
        "schema": "fold-protein-blind-evaluation/v1",
        "status": "completed",
        "run_id": seal["run_id"],
        "execution": "post-seal structural comparison",
        "seal_sha256": sha256(sealed_dir / "seal.json"),
        "target_id": target_path.name,
        "target_sha256": target_hash,
        "matched_ca_atoms": matched,
        "tm_score": tm_score,
        "ca_drmsd_angstrom": drmsd,
        "sequence_length": len(states["sequence"]),
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
    print(json.dumps(evaluate(args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
