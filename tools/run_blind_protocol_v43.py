#!/usr/bin/env python3
"""Run and seal the complete V43 One-cycle graph frontier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.blind_24_lattice_selector_v43 import select_state_frontier_v43
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]
PARENT_DIR = ROOT / "verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit_states(sequence: str, states: list[int], path: Path) -> None:
    write_pdb(build_backbone_coordinates(
        sequence,
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states],
    ), path)


def run_protocol_v43(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v43":
        raise ValueError("unsupported V43 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V43 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V43 source drift: {relative}")
    parent_binding = {
        "seal_sha256": sha256(PARENT_DIR / "seal.json"),
        "frontier_sha256": sha256(PARENT_DIR / "frontier.json"),
    }
    if manifest.get("parent_v42") != parent_binding:
        raise RuntimeError("V43 V42 parent drifted")
    parent = json.loads((PARENT_DIR / "frontier.json").read_text())

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v43-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_frontier_v43(selector_input["sequence"], parent)
        rows, pdb_hashes = [], {}
        for row in result["frontier"]:
            name = f'prediction_mask_{row["mask"]}.pdb'
            emit_states(selector_input["sequence"], row["states"], stage / name)
            pdb_hashes[name] = sha256(stage / name)
            rows.append({**row, "prediction_pdb": name,
                         "prediction_pdb_sha256": pdb_hashes[name]})
        record = {
            "schema": "fold-protein-selected-frontier/v43",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": selector_input["sequence"],
            "block_count": result["block_count"],
            "component_cube_candidates": result["component_cube_candidates"],
            "cycle_rank_target": result["cycle_rank_target"],
            "cycle_rank_census": result["cycle_rank_census"],
            "one_cycle_frontier_count": result["one_cycle_frontier_count"],
            "frontier": rows,
        }
        frontier_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "frontier.json").write_bytes(frontier_bytes)
        seal = {
            "schema": "fold-protein-blind-seal/v43",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "complete 8,192-row graph cycle-rank census and complete One-cycle frontier",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "selector_input_sha256": hashlib.sha256(input_raw).hexdigest(),
            "source_sha256": manifest["source_sha256"],
            "parent_v42": parent_binding,
            "frontier_sha256": hashlib.sha256(frontier_bytes).hexdigest(),
            "prediction_pdb_sha256": pdb_hashes,
            "component_cube_candidates": result["component_cube_candidates"],
            "cycle_rank_target": result["cycle_rank_target"],
            "one_cycle_frontier_count": result["one_cycle_frontier_count"],
            "frontier_masks": [row["mask"] for row in rows],
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
    print(json.dumps(run_protocol_v43(
        args.manifest, args.selector_input, args.output_dir
    ), sort_keys=True))


if __name__ == "__main__":
    main()
