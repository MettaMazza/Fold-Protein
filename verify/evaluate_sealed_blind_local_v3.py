#!/usr/bin/env python3
"""Post-seal same-index local evaluation for a selector-v3 prediction.

The v3 seal is verified before the target path is resolved or read. Every
contiguous window of the declared length is reported; no target measurement is
fed back to selection and no candidate cap is applied.
"""
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
from verify.evaluate_sealed_blind_v3 import verify_v3_seal  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kabsch_rmsd(prediction: np.ndarray, target: np.ndarray) -> float:
    left = prediction - prediction.mean(axis=0)
    right = target - target.mean(axis=0)
    u, _, vt = np.linalg.svd(left.T @ right)
    sign = np.linalg.det(u @ vt)
    correction = np.eye(3)
    correction[-1, -1] = -1.0 if sign < 0 else 1.0
    rotation = u @ correction @ vt
    aligned = left @ rotation
    return float(np.sqrt(np.mean(np.sum((aligned - right) ** 2, axis=1))))


def distance_rmsd(prediction: np.ndarray, target: np.ndarray) -> float:
    pred_dist = np.linalg.norm(
        prediction[:, None, :] - prediction[None, :, :], axis=2)
    target_dist = np.linalg.norm(
        target[:, None, :] - target[None, :, :], axis=2)
    return float(np.sqrt(np.mean((pred_dist - target_dist) ** 2)))


def evaluate(manifest: Path, sealed_dir: Path, target_path: Path,
             output_path: Path, window_length: int) -> dict:
    if window_length <= 0:
        raise ValueError("window length must be positive")
    seal, states = verify_v3_seal(manifest, sealed_dir)

    # Target access starts only after the complete seal verification above.
    target_path = target_path.resolve()
    prediction_path = sealed_dir.resolve() / "prediction.pdb"
    prediction = parse_ca(str(prediction_path))
    target = parse_ca(str(target_path))
    matched = min(len(prediction), len(target), len(states["sequence"]))
    if matched < window_length:
        raise RuntimeError("window exceeds matched sealed coordinates")
    prediction = prediction[:matched]
    target = target[:matched]
    sequence = states["sequence"][:matched]

    windows = []
    for start in range(matched - window_length + 1):
        end = start + window_length
        pred_window = prediction[start:end]
        target_window = target[start:end]
        windows.append({
            "residue_positions_one_based": [start + 1, end],
            "sequence": sequence[start:end],
            "local_tm_score": float(compute_tm(pred_window, target_window)),
            "kabsch_ca_rmsd_angstrom": kabsch_rmsd(pred_window, target_window),
            "ca_drmsd_angstrom": distance_rmsd(pred_window, target_window),
        })

    minimum_rmsd = min(
        windows,
        key=lambda row: (row["kabsch_ca_rmsd_angstrom"],
                         row["residue_positions_one_based"]),
    )
    maximum_tm = max(
        windows,
        key=lambda row: (row["local_tm_score"],
                         [-held for held in row["residue_positions_one_based"]]),
    )
    result = {
        "schema": "fold-protein-blind-local-evaluation/v3",
        "status": "completed",
        "run_id": seal["run_id"],
        "execution": "post-seal same-index contiguous local comparison",
        "seal_sha256": sha256(sealed_dir.resolve() / "seal.json"),
        "prediction_pdb_sha256": sha256(prediction_path),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "matched_ca_atoms": matched,
        "window_length_residues": window_length,
        "window_count": len(windows),
        "window_rule": (
            "After complete seal verification, report every same-index "
            "contiguous window; no target measurement enters selection."
        ),
        "minimum_kabsch_rmsd_window": minimum_rmsd,
        "maximum_local_tm_window": maximum_tm,
        "windows": windows,
        "provenance": {
            "origin": "Codex-authored post-seal measurement",
            "agent": "Codex",
            "model": "gpt-5.6-sol",
            "reasoning_level": "high",
            "authority": "Maria Smith owns publishable conclusions and project direction.",
        },
        "source_sha256": {str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
    }
    output_path = output_path.resolve()
    stage = output_path.with_name(output_path.name + ".building")
    stage.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    stage.replace(output_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--window-length", type=int, default=3)
    args = parser.parse_args()
    result = evaluate(
        args.manifest, args.sealed_dir, args.target, args.output,
        args.window_length)
    print(json.dumps({
        "schema": result["schema"],
        "status": result["status"],
        "run_id": result["run_id"],
        "window_count": result["window_count"],
        "minimum_kabsch_rmsd_window": result["minimum_kabsch_rmsd_window"],
        "maximum_local_tm_window": result["maximum_local_tm_window"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
