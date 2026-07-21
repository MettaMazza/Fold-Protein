#!/usr/bin/env python3
"""Run and seal V37 unordered whole-chain generator reconciliation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v34 import closed_angle_domain
from tools.blind_24_lattice_selector_v36 import COMPLETE_CHAIN_CANDIDATES
from tools.blind_24_lattice_selector_v37 import (
    BINARY_COUNT,
    COLOUR_COUNT,
    PARTITION_SPAN,
    select_state_path_v37,
)
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_protocol_v37(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v37":
        raise ValueError("unsupported selector-v37 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V37 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V37 protocol source drift: {relative}")
    expected_config = {
        "candidate_domain": closed_angle_domain(),
        "candidate_domain_count": 2,
        "complete_chain_candidates": COMPLETE_CHAIN_CANDIDATES,
        "partition_generators": [BINARY_COUNT, COLOUR_COUNT],
        "partition_span": PARTITION_SPAN,
        "mode_assignment": None,
        "required_qualifying_candidates": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("V37 selector configuration drift")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v37-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        sequence = str(selector_input["sequence"]).upper()
        result = select_state_path_v37(sequence)
        record = {
            "schema": "fold-protein-selected-states/v37",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": sequence,
            "states": result["states"],
            "modes": result["modes"],
            "closed_domain": result["closed_domain"],
            "complete_chain_candidates": result["complete_chain_candidates"],
            "partition_span": result["partition_span"],
            "partition_unit_count": result["partition_unit_count"],
            "expected_unordered_mode_census": result["expected_unordered_mode_census"],
            "qualifying_candidates": result["qualifying_candidates"],
            "census_trace": result["census_trace"],
            "selected_direction": result["selected_direction"],
            "selected_context": result["selected_context"],
            "final_key": result["final_key"],
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v37",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "complete V36 grammar reconciled by the unordered engine-closed binary-colour census",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "candidate_domain": result["closed_domain"],
            "complete_chain_candidates": COMPLETE_CHAIN_CANDIDATES,
            "partition_span": PARTITION_SPAN,
            "partition_unit_count": result["partition_unit_count"],
            "expected_unordered_mode_census": result["expected_unordered_mode_census"],
            "qualifying_candidates": result["qualifying_candidates"],
            "selected_direction": result["selected_direction"],
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
    print(json.dumps(run_protocol_v37(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
