#!/usr/bin/env python3
"""Run and seal V41 complete connected-component cube reconciliation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v41 import (
    EXPECTED_COMPONENTS,
    EXPECTED_CUBE_CANDIDATES,
    EXPECTED_DISAGREEMENTS,
    select_state_path_v41,
)
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]
PARENT_DIR = ROOT / "verify/development_runs/ubiquitin_v40_lineage_paired_fixed_point_l76_20260721"
PARENT_MANIFEST = ROOT / "verify/blind_selector_v40.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_parent(manifest: dict) -> dict:
    required = {
        "manifest_sha256": sha256_file(PARENT_MANIFEST),
        "seal_sha256": sha256_file(PARENT_DIR / "seal.json"),
        "selected_states_sha256": sha256_file(PARENT_DIR / "selected_states.json"),
        "prediction_pdb_sha256": sha256_file(PARENT_DIR / "prediction.pdb"),
        "selector_input_sha256": sha256_file(PARENT_DIR / "selector_input.json"),
    }
    if manifest.get("parent_v40") != required:
        raise RuntimeError("V41 registered V40 parent binding drifted")
    seal = json.loads((PARENT_DIR / "seal.json").read_text())
    if (seal.get("schema") != "fold-protein-blind-seal/v40"
            or seal.get("status") != "completed"
            or seal.get("selected_states_sha256") != required["selected_states_sha256"]):
        raise RuntimeError("V41 V40 parent seal is invalid")
    return json.loads((PARENT_DIR / "selected_states.json").read_text())


def run_protocol_v41(manifest_path: Path, input_path: Path, output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = map(Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(output_dir)
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v41":
        raise ValueError("unsupported V41 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V41 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"V41 protocol source drift: {relative}")
    expected_config = {
        "disagreement_count": 42,
        "component_count": 13,
        "component_cube_candidates": 8192,
        "paired_state_count": 576,
        "causal_direction": "n_to_c",
        "parallel_workers": 24,
        "beam": None,
        "cutoff": None,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("V41 selector configuration drift")
    if (EXPECTED_DISAGREEMENTS, EXPECTED_COMPONENTS, EXPECTED_CUBE_CANDIDATES) != (42, 13, 8192):
        raise RuntimeError("V41 registered runtime census drifted")
    parent = verify_parent(manifest)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v41-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        sequence = str(selector_input["sequence"]).upper()
        result = select_state_path_v41(sequence, parent)
        record = {
            "schema": "fold-protein-selected-states/v41",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": sequence,
            "states": result["states"],
            "parent_v40_states": result["parent_v40_states"],
            "parent_fixed_points": result["parent_fixed_points"],
            "disagreement_count": result["disagreement_count"],
            "components": result["components"],
            "component_count": result["component_count"],
            "component_cube_candidates": result["component_cube_candidates"],
            "component_cube_trace": result["component_cube_trace"],
            "selected_component_mask": result["selected_component_mask"],
            "selected_component_rank": result["selected_component_rank"],
            "paired_fixed_point": result["paired_fixed_point"],
            "cube_evaluations": result["cube_evaluations"],
            "paired_evaluations": result["paired_evaluations"],
            "total_evaluations": result["total_evaluations"],
            "parallel_workers": result["parallel_workers"],
            "final_key": result["final_key"],
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v41",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "complete 8192-row connected-component cube followed by complete paired-state fixed-point descent",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "parent_v40": manifest["parent_v40"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "disagreement_count": result["disagreement_count"],
            "component_count": result["component_count"],
            "component_cube_candidates": result["component_cube_candidates"],
            "total_evaluations": result["total_evaluations"],
        }
        (stage / "seal.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
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
    print(json.dumps(run_protocol_v41(args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
