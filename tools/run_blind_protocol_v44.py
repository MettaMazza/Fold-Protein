#!/usr/bin/env python3
"""Run and seal the complete V44 connected cycle-to-One fixed-point frontier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.blind_24_lattice_selector_v44 import select_state_frontier_v44
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]
V42_DIR = ROOT / "verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721"
V43_DIR = ROOT / "verify/development_runs/ubiquitin_v43_one_cycle_frontier_l76_20260721"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit_states(sequence: str, states: list[int], path: Path) -> None:
    write_pdb(build_backbone_coordinates(
        sequence,
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states],
    ), path)


def run_protocol_v44(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v44":
        raise ValueError("unsupported V44 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V44 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V44 source drift: {relative}")
    parent_v42 = {
        "seal_sha256": sha256(V42_DIR / "seal.json"),
        "frontier_sha256": sha256(V42_DIR / "frontier.json"),
    }
    parent_v43 = {
        "seal_sha256": sha256(V43_DIR / "seal.json"),
        "frontier_sha256": sha256(V43_DIR / "frontier.json"),
    }
    if manifest.get("parent_v42") != parent_v42:
        raise RuntimeError("V44 V42 parent drifted")
    if manifest.get("parent_v43") != parent_v43:
        raise RuntimeError("V44 V43 parent drifted")
    parent = json.loads((V42_DIR / "frontier.json").read_text())

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-v44-sealed-", dir=output_dir.parent
    ))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_frontier_v44(selector_input["sequence"], parent)
        rows, pdb_hashes = [], {}
        for index, row in enumerate(result["frontier"]):
            name = f"prediction_fixed_point_{index:02d}.pdb"
            emit_states(selector_input["sequence"], row["states"], stage / name)
            pdb_hashes[name] = sha256(stage / name)
            rows.append({
                **row,
                "prediction_pdb": name,
                "prediction_pdb_sha256": pdb_hashes[name],
            })
        record = {
            "schema": "fold-protein-selected-frontier/v44",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": selector_input["sequence"],
            "connected_parent_count": result["connected_parent_count"],
            "paired_state_count": result["paired_state_count"],
            "causal_direction": result["causal_direction"],
            "cycle_rank_target": result["cycle_rank_target"],
            "block_count": result["block_count"],
            "fixed_point_trace": result["fixed_point_trace"],
            "distinct_fixed_points": result["distinct_fixed_points"],
            "frontier": rows,
            "total_evaluations": result["total_evaluations"],
            "total_connected_evaluations": result[
                "total_connected_evaluations"
            ],
            "parallel_workers": result["parallel_workers"],
        }
        frontier_bytes = (
            json.dumps(record, indent=2, sort_keys=True) + "\n"
        ).encode()
        (stage / "frontier.json").write_bytes(frontier_bytes)
        seal = {
            "schema": "fold-protein-blind-seal/v44",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "complete connected-parent 576-state N-to-C cycle-to-One fixed-point frontier",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "selector_input_sha256": hashlib.sha256(input_raw).hexdigest(),
            "source_sha256": manifest["source_sha256"],
            "parent_v42": parent_v42,
            "parent_v43": parent_v43,
            "frontier_sha256": hashlib.sha256(frontier_bytes).hexdigest(),
            "prediction_pdb_sha256": pdb_hashes,
            "connected_parent_count": result["connected_parent_count"],
            "paired_state_count": result["paired_state_count"],
            "cycle_rank_target": result["cycle_rank_target"],
            "distinct_fixed_points": result["distinct_fixed_points"],
            "total_evaluations": result["total_evaluations"],
            "total_connected_evaluations": result[
                "total_connected_evaluations"
            ],
        }
        (stage / "seal.json").write_text(
            json.dumps(seal, indent=2, sort_keys=True) + "\n"
        )
        os.replace(stage, output_dir)
        return seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("selector_input", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run_protocol_v44(
        args.manifest, args.selector_input, args.output_dir
    ), sort_keys=True))


if __name__ == "__main__":
    main()
