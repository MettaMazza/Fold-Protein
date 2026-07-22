#!/usr/bin/env python3
"""Verify the material seal, then measure its frozen L76 structure."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from calculate_tm import compute_tm, parse_ca
from verify.evaluate_sealed_blind_local_v11 import kabsch_rmsd


ROOT = Path(__file__).resolve().parents[1]


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_pair_distance_rmsd(prediction: np.ndarray,
                               target: np.ndarray) -> float:
    deltas = []
    for left in range(len(prediction)):
        for right in range(left + 1, len(prediction)):
            deltas.append(
                np.linalg.norm(prediction[right] - prediction[left])
                - np.linalg.norm(target[right] - target[left])
            )
    return float(np.sqrt(np.mean(np.asarray(deltas) ** 2)))


def verify_material_seal(manifest_path: Path, sealed_dir: Path):
    manifest_path = manifest_path.resolve()
    sealed_dir = sealed_dir.resolve()
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    seal = json.loads((sealed_dir / "seal.json").read_text())
    selected = json.loads((sealed_dir / "selected_states.json").read_text())
    if (manifest.get("schema") != "fold-protein-material-protocol/v1"
            or seal.get("schema") != "fold-protein-material-seal/v1"
            or selected.get("schema") != "fold-protein-material-states/v1"):
        raise RuntimeError("material seal schema mismatch")
    if seal["protocol_manifest_sha256"] != sha256(manifest_raw).hexdigest():
        raise RuntimeError("material manifest seal drifted")
    for relative, expected in seal["source_sha256"].items():
        if file_sha256(ROOT / relative) != expected:
            raise RuntimeError(f"sealed material source drift: {relative}")
    if file_sha256(sealed_dir / "selected_states.json") != seal[
            "selected_states_sha256"]:
        raise RuntimeError("sealed material states drifted")
    if file_sha256(sealed_dir / "prediction.pdb") != seal[
            "prediction_pdb_sha256"]:
        raise RuntimeError("sealed material prediction drifted")
    required = {
        "complete_raw_state_candidates": 43776,
        "complete_raw_signature_matches": 122,
        "unique_material_states": 76,
        "window_geometry_checks": 74,
        "quartet_geometry_checks": 73,
        "contact_relation_checks": 40,
        "long_range_orientation_checks": 2628,
        "candidate_orderings": 0,
        "weights": 0,
        "fitted_parameters": 0,
        "runtime_target_accesses": 0,
    }
    for key, expected in required.items():
        if seal.get(key) != expected or selected.get(key) != expected:
            raise RuntimeError(f"sealed material census drifted: {key}")
    return seal, selected


def evaluate_material_v1(manifest_path: Path, sealed_dir: Path,
                         target_path: Path, output_path: Path):
    seal, selected = verify_material_seal(manifest_path, sealed_dir)
    # Experimental target access begins only after the complete source-bound
    # structure, state trace and seal have passed verification above.
    prediction = parse_ca(str(sealed_dir / "prediction.pdb"))
    target = parse_ca(str(target_path.resolve()))
    matched = min(len(prediction), len(target))
    prediction, target = prediction[:matched], target[:matched]
    result = {
        "schema": "fold-protein-material-evaluation/v1",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "run_id": seal["run_id"],
        "seal_sha256": file_sha256(sealed_dir / "seal.json"),
        "prediction_pdb_sha256": seal["prediction_pdb_sha256"],
        "target_id": target_path.name,
        "target_sha256": file_sha256(target_path.resolve()),
        "matched_ca_atoms": matched,
        "tm_score": float(compute_tm(prediction, target)),
        "ca_drmsd_angstrom": unique_pair_distance_rmsd(prediction, target),
        "ca_drmsd_convention": "RMS over unique unordered non-self C-alpha pairs",
        "kabsch_ca_rmsd_angstrom": kabsch_rmsd(prediction, target),
        "complete_raw_state_candidates": seal[
            "complete_raw_state_candidates"
        ],
        "unique_material_states": seal["unique_material_states"],
        "elapsed_seconds": seal["elapsed_seconds"],
        "maximum_resident_set_bytes": seal["maximum_resident_set_bytes"],
        "memory_platform": seal["memory_platform"],
        "evaluator_sha256": file_sha256(Path(__file__).resolve()),
        "provenance": {
            "author": "OpenAI Codex",
            "model": "GPT-5",
            "reasoning_level": "high",
        },
    }
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_material_v1(
        args.manifest, args.sealed_dir, args.target, args.output
    ), sort_keys=True))


if __name__ == "__main__":
    main()
