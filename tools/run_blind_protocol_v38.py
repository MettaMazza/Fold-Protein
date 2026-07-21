#!/usr/bin/env python3
"""Run and seal V38 complete coordinate-axis fixed-point descent."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v38 import (
    AXIS_ORDERS,
    AXIS_VALUE_COUNT,
    CHAIN_DIRECTIONS,
    DESCENT_ORDERS,
    PAIRED_STATE_COUNT,
    select_state_path_v38,
)
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_protocol_v38(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v38":
        raise ValueError("unsupported selector-v38 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V38 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V38 protocol source drift: {relative}")
    expected_config = {
        "axis_value_count": AXIS_VALUE_COUNT,
        "coordinate_axis_count": 2,
        "paired_state_count": PAIRED_STATE_COUNT,
        "chain_direction_count": len(CHAIN_DIRECTIONS),
        "axis_order_count": len(AXIS_ORDERS),
        "descent_order_count": len(DESCENT_ORDERS),
        "parallel_workers": len(DESCENT_ORDERS),
        "coordinate_candidates_per_scan": AXIS_VALUE_COUNT,
        "convergence": "strict finite total-order fixed point",
        "beam": None,
        "cutoff": None,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("V38 selector configuration drift")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v38-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        sequence = str(selector_input["sequence"]).upper()
        result = select_state_path_v38(sequence)
        record = {
            "schema": "fold-protein-selected-states/v38",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": sequence,
            "states": result["states"],
            "parent_states": result["parent_states"],
            "axis_value_count": result["axis_value_count"],
            "paired_state_count": result["paired_state_count"],
            "descent_order_count": result["descent_order_count"],
            "parallel_workers": result["parallel_workers"],
            "descent_trace": result["descent_trace"],
            "total_coordinate_evaluations": result["total_coordinate_evaluations"],
            "selected_descent": result["selected_descent"],
            "final_key": result["final_key"],
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v38",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "complete four-order one-coordinate descent to strict finite fixed points",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "axis_value_count": AXIS_VALUE_COUNT,
            "paired_state_count": PAIRED_STATE_COUNT,
            "descent_order_count": len(DESCENT_ORDERS),
            "parallel_workers": result["parallel_workers"],
            "total_coordinate_evaluations": result["total_coordinate_evaluations"],
            "selected_descent": result["selected_descent"],
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
    print(json.dumps(run_protocol_v38(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
