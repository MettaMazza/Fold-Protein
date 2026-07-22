#!/usr/bin/env python3
"""Build a hash-bound index of empirical positive-frontier recoveries."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_view(row: dict) -> dict:
    return {
        "candidate_index": row["candidate_index"],
        "candidate_label": row.get("candidate_label"),
        "selected_emission": row["selected_emission"],
        "states_sha256": row.get("states_sha256", row.get("path_sha256")),
        "prediction_pdb_sha256": row.get("prediction_pdb_sha256"),
        "tm_score": row["tm_score"],
        "ca_drmsd_angstrom": row["ca_drmsd_angstrom"],
    }


def build(output: Path) -> dict:
    output = output.resolve()
    patterns = (
        "verify/development_runs/*/reconstructed_frontier_v1/evaluation.json",
        "verify/development_runs/*/reconstructed_final_beam_v1/evaluation.json",
        "verify/development_runs/*/preserved_frontier_postseal/evaluation.json",
        "verify/development_runs/*/fixed_point_postseal.json",
        "verify/development_runs/*/complete_cube_postseal.json",
    )
    evidence_paths = sorted({
        path for pattern in patterns for path in ROOT.glob(pattern)
    })
    evidence_paths = [
        path for path in evidence_paths
        if not (
            path.parent.name == "reconstructed_frontier_v1"
            and (path.parent.parent / "reconstructed_final_beam_v1/evaluation.json").is_file()
        )
    ]
    recoveries = []
    for path in evidence_paths:
        evidence = json.loads(path.read_text())
        raw_rows = evidence.get("frontier", evidence.get("fixed_points"))
        rows = []
        for index, row in enumerate(raw_rows):
            normalized = dict(row)
            normalized["candidate_index"] = row.get(
                "candidate_index", row.get("mask", index)
            )
            normalized["candidate_label"] = row.get("seed")
            normalized["selected_emission"] = row.get(
                "selected_emission", row.get("mask") == 0
            )
            rows.append(normalized)
        selected_rows = [row for row in rows if row["selected_emission"]]
        if len(selected_rows) != 1:
            raise RuntimeError(f"expected one selected emission in {path}")
        selected = selected_rows[0]
        max_tm = max(rows, key=lambda row: row["tm_score"])
        min_drmsd = min(rows, key=lambda row: row["ca_drmsd_angstrom"])
        dual = [
            row for row in rows
            if row["tm_score"] > selected["tm_score"]
            and row["ca_drmsd_angstrom"] < selected["ca_drmsd_angstrom"]
        ]
        recoveries.append({
            "run_id": evidence["run_id"],
            "evaluation_path": str(path.relative_to(ROOT)),
            "evaluation_sha256": sha256(path),
            "frontier_seal_sha256": evidence.get(
                "frontier_seal_sha256", evidence.get(
                    "frontier_replay_sha256", evidence.get("seal_sha256")
                )
            ),
            "source_seal_sha256": evidence.get("source_seal_sha256"),
            "target_sha256": evidence["target_sha256"],
            "candidate_count": len(rows),
            "selected_emission": row_view(selected),
            "maximum_tm_candidate": row_view(max_tm),
            "minimum_drmsd_candidate": row_view(min_drmsd),
            "strict_dual_improvement_count": len(dual),
            "strict_dual_improvements": [row_view(row) for row in dual],
        })
    summary = {
        "schema": "fold-protein-positive-frontier-recovery-summary/v1",
        "status": "completed",
        "result_type": "cumulative development evidence index",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions",
        "recovery_count": len(recoveries),
        "candidate_count": sum(row["candidate_count"] for row in recoveries),
        "recoveries_with_strict_dual_improvement": sum(
            row["strict_dual_improvement_count"] > 0 for row in recoveries
        ),
        "recoveries": recoveries,
    }
    if output.exists():
        existing = json.loads(output.read_text())
        if existing == summary:
            return summary
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output), sort_keys=True))


if __name__ == "__main__":
    main()
