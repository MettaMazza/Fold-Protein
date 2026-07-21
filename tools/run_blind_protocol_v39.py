#!/usr/bin/env python3
"""Run and seal V39 peptide-causal reconciliation from sealed V38 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v39 import (
    CAUSAL_AXIS_ORDER,
    CAUSAL_DIRECTION,
    select_state_path_v39,
)
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]
PARENT_DIR = ROOT / "verify/development_runs/ubiquitin_v38_coordinate_fixed_point_l76_20260721"
PARENT_MANIFEST = ROOT / "verify/blind_selector_v38.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_registered_v38_parent(manifest: dict) -> dict:
    parent_binding = manifest.get("parent_v38", {})
    required = {
        "manifest_sha256": sha256_file(PARENT_MANIFEST),
        "seal_sha256": sha256_file(PARENT_DIR / "seal.json"),
        "selected_states_sha256": sha256_file(PARENT_DIR / "selected_states.json"),
        "prediction_pdb_sha256": sha256_file(PARENT_DIR / "prediction.pdb"),
        "selector_input_sha256": sha256_file(PARENT_DIR / "selector_input.json"),
    }
    if parent_binding != required:
        raise RuntimeError("V39 registered V38 parent binding drifted")
    seal = json.loads((PARENT_DIR / "seal.json").read_text())
    if (seal.get("schema") != "fold-protein-blind-seal/v38"
            or seal.get("status") != "completed"
            or seal.get("selected_states_sha256") != required["selected_states_sha256"]
            or seal.get("prediction_pdb_sha256") != required["prediction_pdb_sha256"]):
        raise RuntimeError("V39 V38 parent seal is invalid")
    return json.loads((PARENT_DIR / "selected_states.json").read_text())


def run_protocol_v39(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v39":
        raise ValueError("unsupported selector-v39 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V39 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V39 protocol source drift: {relative}")
    expected_config = {
        "parent_fixed_points": 4,
        "causal_direction": CAUSAL_DIRECTION,
        "causal_axis_order": list(CAUSAL_AXIS_ORDER),
        "phi_event_rank": 3,
        "psi_event_rank": 4,
        "qualifying_fixed_points": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("V39 selector configuration drift")
    parent = verify_registered_v38_parent(manifest)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v39-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        sequence = str(selector_input["sequence"]).upper()
        result = select_state_path_v39(sequence, parent)
        record = {
            "schema": "fold-protein-selected-states/v39",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": sequence,
            "states": result["states"],
            "parent_selected_states": result["parent_selected_states"],
            "parent_v38_selected_states_sha256": manifest["parent_v38"]["selected_states_sha256"],
            "parent_fixed_point_count": result["parent_fixed_point_count"],
            "causal_direction": result["causal_direction"],
            "causal_axis_order": result["causal_axis_order"],
            "causal_event_ranks": result["causal_event_ranks"],
            "selected_parent_sweeps": result["selected_parent_sweeps"],
            "selected_parent_evaluations": result["selected_parent_evaluations"],
            "final_key": result["final_key"],
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v39",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "unique N-to-C phi-before-psi causal fixed point extracted from sealed V38 grammar",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "parent_v38": manifest["parent_v38"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "parent_fixed_point_count": result["parent_fixed_point_count"],
            "causal_direction": result["causal_direction"],
            "causal_axis_order": result["causal_axis_order"],
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
    print(json.dumps(run_protocol_v39(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
