#!/usr/bin/env python3
"""Compare the already sealed v11/v12 applied paths and post-seal windows."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "verify/development_runs"
V11 = RUNS / "ubiquitin_v11_hbond_assembly_l24_20260719"
V12 = RUNS / "ubiquitin_v12_topology_hbond_l24_20260719"
OUTPUT = RUNS / "ubiquitin_v12_topology_hbond_l24_20260719" / "v11_v12_state_delta.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sealed(run: Path) -> tuple[dict, dict, str]:
    seal_path = run / "seal.json"
    states_path = run / "selected_states.json"
    seal = json.loads(seal_path.read_text())
    states = json.loads(states_path.read_text())
    if seal["status"] != "completed":
        raise RuntimeError(f"not sealed: {run}")
    if seal["selected_states_sha256"] != sha256(states_path):
        raise RuntimeError(f"selected-state seal mismatch: {run}")
    if states["status"] != "completed":
        raise RuntimeError(f"incomplete selected path: {run}")
    return seal, states, sha256(seal_path)


def load_local(run: Path, length: int, seal_hash: str) -> dict:
    path = run / f"local_windows_l{length}.json"
    receipt = json.loads(path.read_text())
    if receipt["status"] != "completed" or receipt["seal_sha256"] != seal_hash:
        raise RuntimeError(f"local receipt does not bind the seal: {path}")
    return receipt


def main() -> None:
    seal11, states11, seal_hash11 = load_sealed(V11)
    seal12, states12, seal_hash12 = load_sealed(V12)
    if states11["sequence"] != states12["sequence"]:
        raise RuntimeError("v11/v12 sequence mismatch")

    changed = [
        {"residue_one_based": index, "v11_state": left, "v12_state": right}
        for index, (left, right) in enumerate(
            zip(states11["states"], states12["states"]), start=1)
        if left != right
    ]
    local = {}
    for length in (3, 4, 5):
        left = load_local(V11, length, seal_hash11)
        right = load_local(V12, length, seal_hash12)
        rows = []
        for before, after in zip(left["windows"], right["windows"]):
            if (before["sequence"], before["residue_positions_one_based"]) != (
                    after["sequence"], after["residue_positions_one_based"]):
                raise RuntimeError("local window identity mismatch")
            delta = after["local_tm_score"] - before["local_tm_score"]
            rows.append({
                "sequence": before["sequence"],
                "residue_positions_one_based": before["residue_positions_one_based"],
                "v11_local_tm": before["local_tm_score"],
                "v12_local_tm": after["local_tm_score"],
                "v12_minus_v11": delta,
            })
        improvements = sorted(rows, key=lambda row: row["v12_minus_v11"], reverse=True)
        local[str(length)] = {
            "windows": len(rows),
            "improved": sum(row["v12_minus_v11"] > 0 for row in rows),
            "unchanged": sum(row["v12_minus_v11"] == 0 for row in rows),
            "regressed": sum(row["v12_minus_v11"] < 0 for row in rows),
            "largest_improvements": improvements[:5],
            "largest_regressions": list(reversed(improvements[-5:])),
        }

    evaluation11 = json.loads((V11 / "evaluation.json").read_text())
    evaluation12 = json.loads((V12 / "evaluation.json").read_text())
    output = {
        "schema": "fold-protein-v11-v12-state-delta/v1",
        "status": "completed",
        "result_type": "measured implementation analysis",
        "benchmark_authority": False,
        "governance_authority": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "origin": "Codex post-seal applied-development analysis",
            "agent": "Codex",
            "model": "gpt-5.6-sol",
            "reasoning_level": "high",
            "authority": "Maria Smith assigns conclusions and full-run timing.",
        },
        "declared_purpose": (
            "Locate the applied path and local-window changes associated with "
            "topology separation so the next target-isolated selector can retain "
            "both whole-prefix assembly and accurate local geometry."
        ),
        "selection_boundary": (
            "Analysis only: both paths were sealed before target access; no "
            "target measurement is fed back into either recorded selection."
        ),
        "sequence_length": len(states11["states"]),
        "state_delta": {
            "changed": len(changed),
            "identical": len(states11["states"]) - len(changed),
            "rows": changed,
        },
        "whole_prefix": {
            "v11_tm_score": evaluation11["tm_score"],
            "v12_tm_score": evaluation12["tm_score"],
            "tm_delta": evaluation12["tm_score"] - evaluation11["tm_score"],
            "v11_ca_drmsd_angstrom": evaluation11["ca_drmsd_angstrom"],
            "v12_ca_drmsd_angstrom": evaluation12["ca_drmsd_angstrom"],
            "ca_drmsd_delta_angstrom": (
                evaluation12["ca_drmsd_angstrom"] - evaluation11["ca_drmsd_angstrom"]
            ),
        },
        "local_window_delta": local,
        "sources": {
            "verify/analyze_v11_v12_state_delta.py": sha256(Path(__file__)),
            "v11/seal.json": seal_hash11,
            "v12/seal.json": seal_hash12,
            "v11/selected_states.json": seal11["selected_states_sha256"],
            "v12/selected_states.json": seal12["selected_states_sha256"],
        },
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": "completed",
        "changed_states": len(changed),
        "whole_prefix_tm_delta": output["whole_prefix"]["tm_delta"],
        "whole_prefix_drmsd_delta": output["whole_prefix"]["ca_drmsd_delta_angstrom"],
        "local": {key: {name: value for name, value in row.items()
                         if name in ("improved", "unchanged", "regressed")}
                  for key, row in local.items()},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
