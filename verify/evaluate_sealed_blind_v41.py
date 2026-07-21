#!/usr/bin/env python3
"""Verify the V41 seal before opening the comparison target."""
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


def verify_v41_seal(manifest_path: Path, sealed_dir: Path) -> tuple[dict, dict]:
    manifest_path, sealed_dir = manifest_path.resolve(), sealed_dir.resolve()
    manifest = json.loads(manifest_path.read_text())
    seal = json.loads((sealed_dir / "seal.json").read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v41" or seal.get("schema") != "fold-protein-blind-seal/v41" or seal.get("status") != "completed":
        raise RuntimeError("invalid V41 seal; target access forbidden")
    required = {
        "protocol_manifest_sha256": sha256(manifest_path),
        "selector_input_sha256": sha256(sealed_dir / "selector_input.json"),
        "selected_states_sha256": sha256(sealed_dir / "selected_states.json"),
        "prediction_pdb_sha256": sha256(sealed_dir / "prediction.pdb"),
    }
    for field, value in required.items():
        if seal.get(field) != value:
            raise RuntimeError(f"V41 seal mismatch: {field}")
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    if (states.get("disagreement_count") != 42 or states.get("component_count") != 13
            or states.get("component_cube_candidates") != 8192
            or len(states.get("component_cube_trace", [])) != 8192
            or states["paired_fixed_point"]["sweeps"][-1]["changed_states"] != 0):
        raise RuntimeError("V41 complete-space identity mismatch")
    for relative, expected in manifest["source_sha256"].items():
        if seal["source_sha256"].get(relative) != expected or sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V41 source drift: {relative}")
    return seal, states


def evaluate_v41(manifest_path: Path, sealed_dir: Path, target_path: Path, output_path: Path) -> dict:
    seal, states = verify_v41_seal(manifest_path, sealed_dir)
    target_path = target_path.resolve()
    pred, target = parse_ca(str(sealed_dir.resolve() / "prediction.pdb")), parse_ca(str(target_path))
    matched = min(len(pred), len(target)); pred, target = pred[:matched], target[:matched]
    pd = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
    td = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    evidence = {
        "schema": "fold-protein-blind-evaluation/v41", "status": "completed",
        "result_type": "cumulative development benchmark", "official_run": False,
        "run_id": seal["run_id"], "execution": "post-seal structural comparison",
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "target_id": target_path.name, "target_sha256": sha256(target_path),
        "matched_ca_atoms": matched, "sequence_length": len(states["sequence"]),
        "tm_score": float(compute_tm(pred, target)),
        "ca_drmsd_angstrom": float(np.sqrt(np.mean((pd - td) ** 2))),
        "states_changed_from_v40": sum(a != b for a, b in zip(states["states"], states["parent_v40_states"])),
        "selected_component_mask": states["selected_component_mask"],
        "paired_fixed_point_sweeps": len(states["paired_fixed_point"]["sweeps"]),
        "cube_evaluations": states["cube_evaluations"],
        "paired_evaluations": states["paired_evaluations"],
        "total_evaluations": states["total_evaluations"],
    }
    if output_path.exists(): raise FileExistsError(output_path)
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("manifest", type=Path); p.add_argument("sealed_dir", type=Path); p.add_argument("target", type=Path); p.add_argument("output", type=Path)
    a = p.parse_args(); print(json.dumps(evaluate_v41(a.manifest, a.sealed_dir, a.target, a.output), sort_keys=True))


if __name__ == "__main__": main()
