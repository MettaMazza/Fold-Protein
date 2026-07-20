#!/usr/bin/env python3
"""Post-seal same-index local evaluation for selector v20."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculate_tm import compute_tm, parse_ca  # noqa: E402
from verify.evaluate_sealed_blind_local_v11 import distance_rmsd, kabsch_rmsd  # noqa: E402
from verify.evaluate_sealed_blind_v20 import sha256, verify_v20_seal  # noqa: E402


def evaluate(manifest: Path, sealed_dir: Path, target_path: Path,
             output_path: Path, window_length: int) -> dict:
    if window_length <= 0:
        raise ValueError("window length must be positive")
    seal, states = verify_v20_seal(manifest, sealed_dir)
    target_path = target_path.resolve()
    prediction_path = sealed_dir.resolve() / "prediction.pdb"
    prediction, target = parse_ca(str(prediction_path)), parse_ca(str(target_path))
    matched = min(len(prediction), len(target), len(states["sequence"]))
    if matched < window_length:
        raise RuntimeError("window exceeds matched sealed coordinates")
    prediction, target = prediction[:matched], target[:matched]
    sequence = states["sequence"][:matched]
    windows = []
    for start in range(matched - window_length + 1):
        end = start + window_length
        pred_window, target_window = prediction[start:end], target[start:end]
        windows.append({
            "residue_positions_one_based": [start + 1, end],
            "sequence": sequence[start:end],
            "local_tm_score": float(compute_tm(pred_window, target_window)),
            "kabsch_ca_rmsd_angstrom": kabsch_rmsd(pred_window, target_window),
            "ca_drmsd_angstrom": distance_rmsd(pred_window, target_window),
        })
    minimum_rmsd = min(windows, key=lambda row: (
        row["kabsch_ca_rmsd_angstrom"], row["residue_positions_one_based"]))
    maximum_tm = max(windows, key=lambda row: (
        row["local_tm_score"], [-value for value in row["residue_positions_one_based"]]))
    result = {
        "schema": "fold-protein-blind-local-evaluation/v20",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
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
            "contiguous window; no target measurement enters selection."),
        "minimum_kabsch_rmsd_window": minimum_rmsd,
        "maximum_local_tm_window": maximum_tm,
        "windows": windows,
        "provenance": {
            "origin": "Codex post-seal cumulative development measurement",
            "agent": "Codex", "model": "gpt-5.6-sol", "reasoning_level": "high",
            "authority": "Maria Smith alone assigns conclusions and official status.",
        },
        "source_sha256": {
            str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
    }
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(f"local evaluation exists: {output_path}")
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--window-length", type=int, default=4)
    args = parser.parse_args()
    result = evaluate(
        args.manifest, args.sealed_dir, args.target, args.output,
        args.window_length)
    print(json.dumps({
        "status": result["status"],
        "window_count": result["window_count"],
        "minimum_kabsch_rmsd_window": result["minimum_kabsch_rmsd_window"],
        "maximum_local_tm_window": result["maximum_local_tm_window"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
