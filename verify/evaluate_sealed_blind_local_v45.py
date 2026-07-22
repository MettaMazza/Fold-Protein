#!/usr/bin/env python3
"""Post-seal same-index local evaluation of every sealed V45 fixed point."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from calculate_tm import compute_tm, parse_ca
from verify.evaluate_sealed_blind_local_v11 import distance_rmsd, kabsch_rmsd
from verify.evaluate_sealed_blind_v45 import verify_v45_seal


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_local_v45(manifest_path: Path, sealed_dir: Path,
                       target_path: Path, output_path: Path,
                       window_lengths: tuple[int, ...]) -> dict:
    sealed_dir = sealed_dir.resolve()
    target_path = target_path.resolve()
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    if (not window_lengths or any(length < 3 for length in window_lengths)
            or tuple(sorted(set(window_lengths))) != window_lengths):
        raise ValueError("V45 local lengths must be unique ascending integers >= 3")
    _, frontier = verify_v45_seal(manifest_path, sealed_dir)
    # Target access begins only after all V45 structures and the complete
    # frontier have passed the source-bound seal checks.
    target = parse_ca(str(target_path))
    sequence = frontier["sequence"]
    candidates = []
    for fixed_point_index, row in enumerate(frontier["frontier"]):
        prediction = parse_ca(str(sealed_dir / row["prediction_pdb"]))
        matched = min(len(prediction), len(target), len(sequence))
        pred, ref = prediction[:matched], target[:matched]
        lengths = []
        for length in window_lengths:
            if length > matched:
                raise RuntimeError("V45 local window exceeds matched coordinates")
            windows = []
            for start in range(matched - length + 1):
                end = start + length
                pred_window, ref_window = pred[start:end], ref[start:end]
                windows.append({
                    "residue_positions_one_based": [start + 1, end],
                    "sequence": sequence[start:end],
                    "local_tm_score": float(
                        compute_tm(pred_window, ref_window)
                    ),
                    "kabsch_ca_rmsd_angstrom": kabsch_rmsd(
                        pred_window, ref_window
                    ),
                    "ca_drmsd_angstrom": distance_rmsd(
                        pred_window, ref_window
                    ),
                })
            lengths.append({
                "window_length_residues": length,
                "window_count": len(windows),
                "maximum_local_tm_window": max(
                    windows,
                    key=lambda item: (
                        item["local_tm_score"],
                        tuple(-value for value in item[
                            "residue_positions_one_based"
                        ]),
                    ),
                ),
                "minimum_kabsch_rmsd_window": min(
                    windows,
                    key=lambda item: (
                        item["kabsch_ca_rmsd_angstrom"],
                        item["residue_positions_one_based"],
                    ),
                ),
                "windows": windows,
            })
        candidates.append({
            "fixed_point_index": fixed_point_index,
            "prediction_pdb_sha256": row["prediction_pdb_sha256"],
            "source_orders": row["source_orders"],
            "lengths": lengths,
        })
    evidence = {
        "schema": "fold-protein-blind-local-evaluation/v45",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "run_id": frontier["run_id"],
        "execution": "post-seal complete same-index local comparison of every V45 fixed point",
        "seal_sha256": sha256(sealed_dir / "seal.json"),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "fixed_point_count": len(candidates),
        "window_lengths": list(window_lengths),
        "window_rule": "Every same-index contiguous window at every registered length is retained; target measurements never enter construction or selection.",
        "candidates": candidates,
        "provenance": {
            "origin": "Codex post-seal cumulative development measurement",
            "agent": "Codex",
            "model": "GPT-5",
            "authority": "Maria Smith alone assigns conclusions and official status."
        },
        "evaluator_sha256": sha256(Path(__file__)),
    }
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--window-lengths", type=int, nargs="+", default=(3, 4, 5, 8, 16, 24)
    )
    args = parser.parse_args()
    result = evaluate_local_v45(
        args.manifest,
        args.sealed_dir,
        args.target,
        args.output,
        tuple(args.window_lengths),
    )
    maxima = []
    for candidate in result["candidates"]:
        for length in candidate["lengths"]:
            maxima.append({
                "fixed_point_index": candidate["fixed_point_index"],
                "window_length_residues": length["window_length_residues"],
                **length["maximum_local_tm_window"],
            })
    print(json.dumps({
        "fixed_point_count": result["fixed_point_count"],
        "window_lengths": result["window_lengths"],
        "maximum_local_tm_window": max(
            maxima, key=lambda item: item["local_tm_score"]
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
