#!/usr/bin/env python3
"""Run and seal V40 complete parent-child paired-state fixed points."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v40 import (
    CAUSAL_DIRECTION,
    LINEAGE_SEED_COUNT,
    PAIRED_STATE_COUNT,
    PARALLEL_WORKERS,
    select_state_path_v40,
)
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]
V38_DIR = ROOT / "verify/development_runs/ubiquitin_v38_coordinate_fixed_point_l76_20260721"
V39_DIR = ROOT / "verify/development_runs/ubiquitin_v39_peptide_causal_l76_20260721"
V38_MANIFEST = ROOT / "verify/blind_selector_v38.json"
V39_MANIFEST = ROOT / "verify/blind_selector_v39.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _parent_binding(directory: Path, manifest: Path) -> dict:
    return {
        "manifest_sha256": sha256_file(manifest),
        "seal_sha256": sha256_file(directory / "seal.json"),
        "selected_states_sha256": sha256_file(directory / "selected_states.json"),
        "prediction_pdb_sha256": sha256_file(directory / "prediction.pdb"),
        "selector_input_sha256": sha256_file(directory / "selector_input.json"),
    }


def verify_registered_lineage(manifest: dict) -> tuple[dict, dict]:
    required_v38 = _parent_binding(V38_DIR, V38_MANIFEST)
    required_v39 = _parent_binding(V39_DIR, V39_MANIFEST)
    if manifest.get("parent_v38") != required_v38:
        raise RuntimeError("V40 registered V38 parent binding drifted")
    if manifest.get("parent_v39") != required_v39:
        raise RuntimeError("V40 registered V39 child binding drifted")
    for label, directory, schema, binding in (
        ("V38", V38_DIR, "fold-protein-blind-seal/v38", required_v38),
        ("V39", V39_DIR, "fold-protein-blind-seal/v39", required_v39),
    ):
        seal = json.loads((directory / "seal.json").read_text())
        if (seal.get("schema") != schema or seal.get("status") != "completed"
                or seal.get("selected_states_sha256") != binding["selected_states_sha256"]
                or seal.get("prediction_pdb_sha256") != binding["prediction_pdb_sha256"]):
            raise RuntimeError(f"V40 {label} lineage seal is invalid")
    v38 = json.loads((V38_DIR / "selected_states.json").read_text())
    v39 = json.loads((V39_DIR / "selected_states.json").read_text())
    if v39.get("parent_selected_states") != v38.get("states"):
        raise RuntimeError("V40 parent-child lineage identity drifted")
    return v38, v39


def run_protocol_v40(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v40":
        raise ValueError("unsupported selector-v40 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V40 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V40 protocol source drift: {relative}")
    expected_config = {
        "lineage_seed_count": 2,
        "paired_state_count": 576,
        "updates_per_residue_across_lineage": 1152,
        "causal_direction": "n_to_c",
        "convergence": "strict finite total-order fixed point",
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
        raise RuntimeError("V40 selector configuration drift")
    if (LINEAGE_SEED_COUNT != 2 or PAIRED_STATE_COUNT != 576
            or CAUSAL_DIRECTION != "n_to_c" or PARALLEL_WORKERS != 24):
        raise RuntimeError("V40 runtime constants drifted")
    v38, v39 = verify_registered_lineage(manifest)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v40-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        sequence = str(selector_input["sequence"]).upper()
        result = select_state_path_v40(sequence, v38, v39)
        record = {
            "schema": "fold-protein-selected-states/v40",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": sequence,
            "states": result["states"],
            "parent_v38_states": result["parent_v38_states"],
            "parent_v39_states": result["parent_v39_states"],
            "lineage_seed_count": result["lineage_seed_count"],
            "paired_state_count": result["paired_state_count"],
            "causal_direction": result["causal_direction"],
            "parallel_workers": result["parallel_workers"],
            "fixed_point_trace": result["fixed_point_trace"],
            "distinct_fixed_points": result["distinct_fixed_points"],
            "selected_fixed_point": result["selected_fixed_point"],
            "total_paired_evaluations": result["total_paired_evaluations"],
            "final_key": result["final_key"],
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v40",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "complete 576-state N-to-C fixed points from both admitted parent-child lineage seeds",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "parent_v38": manifest["parent_v38"],
            "parent_v39": manifest["parent_v39"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "lineage_seed_count": result["lineage_seed_count"],
            "paired_state_count": result["paired_state_count"],
            "causal_direction": result["causal_direction"],
            "distinct_fixed_points": result["distinct_fixed_points"],
            "total_paired_evaluations": result["total_paired_evaluations"],
        }
        (stage / "seal.json").write_text(
            json.dumps(seal, indent=2, sort_keys=True) + "\n")
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
    print(json.dumps(run_protocol_v40(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
