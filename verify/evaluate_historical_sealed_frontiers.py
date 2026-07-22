#!/usr/bin/env python3
"""Replay and measure every candidate already bound inside a historical seal.

This evaluator never changes selection. It first verifies the original V36 or
V38 pre-comparison seal, deterministically emits every state path already bound
inside that seal, and records the complete replay frontier before opening the
comparison target. Post-seal scores therefore describe preserved candidates;
they cannot select or retroactively alter them.
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
from tools.blind_24_lattice_selector_v3 import (  # noqa: E402
    CANONICAL_STATE,
    angles_for_state,
)
from tools.protein_backbone_geometry_v1 import (  # noqa: E402
    build_backbone_coordinates,
    write_pdb,
)
from verify.evaluate_sealed_blind_v36 import verify_v36_seal  # noqa: E402
from verify.evaluate_sealed_blind_v38 import verify_v38_seal  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_states(path: list[int], sequence_length: int) -> list[int]:
    states = list(path)
    if len(states) == sequence_length - 1:
        states.append(CANONICAL_STATE)
    if len(states) != sequence_length:
        raise RuntimeError("sealed frontier path has the wrong length")
    return states


def emit_path(sequence: str, path: list[int], output_path: Path) -> None:
    states = canonical_states(path, len(sequence))
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    write_pdb(build_backbone_coordinates(sequence, phi, psi), output_path)


def v36_rows(states: dict) -> list[dict]:
    rows = []
    for index, trace in enumerate(states["reconciliation_trace"]):
        rows.append({
            "candidate_index": index,
            "direction": trace["direction"],
            "context": trace["context"],
            "rank_key": trace["key"],
            "path": trace["path"],
            "selected_emission": (
                trace["direction"] == states["selected_direction"]
                and trace["context"] == states["selected_context"]
            ),
        })
    if len(rows) != 16 or sum(row["selected_emission"] for row in rows) != 1:
        raise RuntimeError("V36 sealed frontier census changed")
    return rows


def v38_rows(states: dict) -> list[dict]:
    rows = []
    for index, trace in enumerate(states["descent_trace"]):
        label = f'{trace["direction"]}:{trace["axis_order"]}'
        rows.append({
            "candidate_index": index,
            "direction": trace["direction"],
            "axis_order": trace["axis_order"],
            "rank_key": trace["rank_key"],
            "sweeps": len(trace["sweeps"]),
            "coordinate_evaluations": trace["evaluations"],
            "path": trace["path"],
            "selected_emission": label == states["selected_descent"],
        })
    if len(rows) != 4 or sum(row["selected_emission"] for row in rows) != 1:
        raise RuntimeError("V38 sealed fixed-point census changed")
    return rows


def verify(version: str, manifest: Path, sealed_dir: Path) -> tuple[dict, dict]:
    if version == "v36":
        return verify_v36_seal(manifest, sealed_dir)
    if version == "v38":
        return verify_v38_seal(manifest, sealed_dir)
    raise ValueError(f"unsupported historical frontier: {version}")


def replay_and_evaluate(version: str, manifest: Path, sealed_dir: Path,
                        target_path: Path, output_dir: Path) -> dict:
    manifest = manifest.resolve()
    sealed_dir = sealed_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)

    original_seal, states = verify(version, manifest, sealed_dir)
    rows = v36_rows(states) if version == "v36" else v38_rows(states)

    output_dir.mkdir(parents=True)
    replay_rows = []
    for row in rows:
        name = f'candidate_{row["candidate_index"]:02d}.pdb'
        pdb_path = output_dir / name
        emit_path(states["sequence"], row["path"], pdb_path)
        replay_row = {key: value for key, value in row.items() if key != "path"}
        replay_row.update({
            "path_sha256": hashlib.sha256(
                json.dumps(row["path"], separators=(",", ":")).encode()
            ).hexdigest(),
            "prediction_pdb": name,
            "prediction_pdb_sha256": sha256(pdb_path),
        })
        replay_rows.append(replay_row)

    replay = {
        "schema": f"fold-protein-{version}-sealed-frontier-replay/v1",
        "status": "replayed_from_original_precomparison_seal",
        "result_type": "cumulative development frontier recovery",
        "official_run": False,
        "run_id": original_seal["run_id"],
        "source_seal_sha256": sha256(sealed_dir / "seal.json"),
        "source_selected_states_sha256": original_seal["selected_states_sha256"],
        "evaluator_sha256": sha256(Path(__file__).resolve()),
        "candidate_count": len(replay_rows),
        "candidates": replay_rows,
    }
    replay_path = output_dir / "frontier_replay.json"
    replay_path.write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n")

    # Target access begins only after every seal-bound candidate has been
    # emitted and the complete deterministic replay has been recorded.
    target_path = target_path.resolve()
    target = parse_ca(str(target_path))
    evaluations = []
    for row in replay_rows:
        prediction = parse_ca(str(output_dir / row["prediction_pdb"]))
        matched = min(len(prediction), len(target))
        pred, ref = prediction[:matched], target[:matched]
        pred_dist = np.linalg.norm(pred[:, None, :] - pred[None, :, :], axis=2)
        ref_dist = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=2)
        evaluations.append({
            **row,
            "matched_ca_atoms": matched,
            "tm_score": float(compute_tm(pred, ref)),
            "ca_drmsd_angstrom": float(
                np.sqrt(np.mean((pred_dist - ref_dist) ** 2))
            ),
        })

    evidence = {
        "schema": f"fold-protein-{version}-sealed-frontier-evaluation/v1",
        "status": "completed",
        "result_type": "post-seal cumulative development frontier recovery",
        "official_run": False,
        "execution": "post-seal comparison of every candidate bound by the original seal",
        "run_id": original_seal["run_id"],
        "source_seal_sha256": replay["source_seal_sha256"],
        "frontier_replay_sha256": sha256(replay_path),
        "target_id": target_path.name,
        "target_sha256": sha256(target_path),
        "candidate_count": len(evaluations),
        "frontier": evaluations,
    }
    evaluation_path = output_dir / "evaluation.json"
    evaluation_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version", choices=("v36", "v38"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = replay_and_evaluate(
        args.version, args.manifest, args.sealed_dir, args.target, args.output_dir
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
