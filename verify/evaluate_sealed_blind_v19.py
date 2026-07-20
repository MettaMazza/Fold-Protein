#!/usr/bin/env python3
"""Verify selector-v19 sealing before opening a comparison target."""
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


def verify_v19_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path, sealed_dir = manifest_path.resolve(), sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v19":
        raise RuntimeError("invalid v19 manifest; target access forbidden")
    seal_path = sealed_dir / "seal.json"
    if not seal_path.is_file():
        raise RuntimeError("missing v19 seal; target access forbidden")
    seal = json.loads(seal_path.read_text())
    if (seal.get("schema") != "fold-protein-blind-seal/v19"
            or seal.get("status") != "completed"):
        raise RuntimeError("invalid v19 seal; target access forbidden")
    for field, path in {
        "protocol_manifest_sha256": manifest_path,
        "selector_input_sha256": sealed_dir / "selector_input.json",
        "selected_states_sha256": sealed_dir / "selected_states.json",
        "prediction_pdb_sha256": sealed_dir / "prediction.pdb",
    }.items():
        if seal.get(field) != sha256(path):
            raise RuntimeError(f"v19 seal mismatch for {field}")
    selector_input = json.loads((sealed_dir / "selector_input.json").read_text())
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    sequence = selector_input.get("sequence", "").upper()
    if (states.get("sequence") != sequence
            or states.get("run_id") != selector_input.get("run_id")
            or len(states.get("states", [])) != len(sequence)):
        raise RuntimeError("v19 input/state identity mismatch")
    if hashlib.sha256(sequence.encode()).hexdigest() != seal.get("sequence_sha256"):
        raise RuntimeError("v19 sequence hash mismatch")
    if (states.get("hard_exclusion_strata") != seal.get("hard_exclusion_strata")
            or states.get("local_graph_pruning") is not False
            or seal.get("local_graph_pruning") is not False):
        raise RuntimeError("v19 global-only graph route mismatch")
    if len(states.get("orientation_trace", [])) != max(0, len(sequence) - 3):
        raise RuntimeError("v19 orientation trace mismatch")
    for field in (
            "charge_census", "steric_census", "hydrogen_bond_census",
            "topology_hydrogen_bond_census", "sidechain_graph_spatial_census"):
        if states.get(field) != seal.get(field):
            raise RuntimeError(f"v19 {field} mismatch")
    if len(states.get("final_relations", {}).get("objectives", [])) != \
            seal.get("constitutional_objectives"):
        raise RuntimeError("v19 objective census mismatch")
    for relative, expected in seal.get("source_sha256", {}).items():
        if (manifest["source_sha256"].get(relative) != expected
                or sha256(ROOT / relative) != expected):
            raise RuntimeError(f"v19 source mismatch for {relative}")
    return seal, states


def evaluate_v19(manifest_path: Path, sealed_dir: Path, target_path: Path,
                 output_path: Path) -> dict:
    seal, states = verify_v19_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    prediction = parse_ca(str(sealed_dir.resolve() / "prediction.pdb"))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target))
    prediction, target = prediction[:matched], target[:matched]
    pred_dist = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    result = {
        "schema": "fold-protein-blind-evaluation/v19",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "run_id": seal["run_id"],
        "execution": "post-seal structural comparison",
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "matched_ca_atoms": matched,
        "tm_score": float(compute_tm(prediction, target)),
        "ca_drmsd_angstrom": float(np.sqrt(np.mean((pred_dist - target_dist) ** 2))),
        "sequence_length": len(states["sequence"]),
    }
    output_path = output_path.resolve()
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
    print(json.dumps(evaluate_v19(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
