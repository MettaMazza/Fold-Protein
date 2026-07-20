#!/usr/bin/env python3
"""Verify selector-v23 sealing before opening a comparison target."""
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


def verify_v23_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path, sealed_dir = manifest_path.resolve(), sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    seal = json.loads((sealed_dir / "seal.json").read_text())
    if (manifest.get("schema") != "fold-protein-blind-selector/v23"
            or seal.get("schema") != "fold-protein-blind-seal/v23"
            or seal.get("status") != "completed"):
        raise RuntimeError("invalid v23 seal; target access forbidden")
    for field, path in {
        "protocol_manifest_sha256": manifest_path,
        "selector_input_sha256": sealed_dir / "selector_input.json",
        "selected_states_sha256": sealed_dir / "selected_states.json",
        "prediction_pdb_sha256": sealed_dir / "prediction.pdb",
    }.items():
        if seal.get(field) != sha256(path):
            raise RuntimeError(f"v23 seal mismatch for {field}")
    selector_input = json.loads((sealed_dir / "selector_input.json").read_text())
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = selector_input.get("sequence", "").upper()
    if (states.get("sequence") != sequence
            or len(states.get("states", [])) != len(sequence)
            or hashlib.sha256(sequence.encode()).hexdigest() != seal.get("sequence_sha256")):
        raise RuntimeError("v23 input/state identity mismatch")
    seed = manifest.get("seed_records", {}).get(seal.get("seed_run_id"), {})
    if (not seed or seed.get("sha256") != seal.get("seed_selected_states_sha256")
            or sha256(ROOT / seed["path"]) != seed["sha256"]):
        raise RuntimeError("v23 registered seed binding mismatch")
    if (len(states.get("domain_trace", [])) != len(sequence) - 1
            or any(row.get("expanded_state_count") != 576
                   for row in states.get("domain_trace", []))):
        raise RuntimeError("v23 complete-domain trace mismatch")
    for relative, expected in seal.get("source_sha256", {}).items():
        if (manifest["source_sha256"].get(relative) != expected
                or sha256(ROOT / relative) != expected):
            raise RuntimeError(f"v23 source mismatch for {relative}")
    return seal, states


def evaluate_v23(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    seal, states = verify_v23_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    prediction = parse_ca(str(sealed_dir.resolve() / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    prediction, target = prediction[:matched], target[:matched]
    pred_dist = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    result = {
        "schema": "fold-protein-blind-evaluation/v23", "status": "completed",
        "result_type": "cumulative development benchmark", "official_run": False,
        "run_id": seal["run_id"], "execution": "post-seal structural comparison",
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "target_id": target_path.name, "target_sha256": sha256(target_path),
        "matched_ca_atoms": matched,
        "tm_score": float(compute_tm(prediction, target)),
        "ca_drmsd_angstrom": float(np.sqrt(np.mean((pred_dist - target_dist) ** 2))),
        "sequence_length": len(states["sequence"]),
    }
    if output_path.exists():
        raise FileExistsError(f"evaluation exists: {output_path}")
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_v23(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
