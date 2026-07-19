#!/usr/bin/env python3
"""Run and immutably seal selector v10 before any target comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

try:
    from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES
    from tools.blind_24_lattice_selector_v7 import (
        BINARY_MODE_COUNT, MODE_CAPACITY, MODE_NAMES)
    from tools.blind_24_lattice_selector_v10 import (
        CHARGE_CENSUS, STERIC_CENSUS, select_state_path_v10)
    from tools.protein_backbone_geometry_v1 import write_pdb
except ImportError:
    from blind_24_lattice_selector_v6 import ORIENTATION_MODES
    from blind_24_lattice_selector_v7 import (
        BINARY_MODE_COUNT, MODE_CAPACITY, MODE_NAMES)
    from blind_24_lattice_selector_v10 import (
        CHARGE_CENSUS, STERIC_CENSUS, select_state_path_v10)
    from protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_protocol_v10(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v10":
        raise ValueError("unsupported selector-v10 manifest")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    input_raw = input_path.read_bytes()
    selector_input = json.loads(input_raw)
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("selector-v10 input must contain exactly run_id and sequence")
    if not all(isinstance(selector_input[key], str) and
               selector_input[key].strip() for key in ("run_id", "sequence")):
        raise ValueError("run_id and sequence must be non-empty strings")
    expected_config = {
        "beam_width": 24,
        "binary_mode_count": BINARY_MODE_COUNT,
        "mode_capacity": MODE_CAPACITY,
        "orientation_residues": 4,
        "overlap_residues": 3,
        "generated_modes": list(MODE_NAMES),
        "constitutional_objectives": 9,
        "sidechain_graphs": 20,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v10 configuration is not the forced census")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v10-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v10(selector_input["sequence"])
        state_record = {
            "schema": "fold-protein-selected-states/v10",
            "run_id": selector_input["run_id"],
            "sequence": selector_input["sequence"].upper(),
            "states": result["states"],
            "score_trace": result["score_trace"],
            "final_relations": result["final_relations"],
            "orientation_modes": result["orientation_modes"],
            "orientation_trace": result["orientation_trace"],
            "mode_capacity": result["mode_capacity"],
            "mode_balance_trace": result["mode_balance_trace"],
            "charge_census": result["charge_census"],
            "steric_census": result["steric_census"],
            "status": "completed",
        }
        state_bytes = (json.dumps(
            state_record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v10",
            "status": "completed",
            "execution": "sequence-only symmetric ordinal selector output",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(
                selector_input["sequence"].upper().encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "orientation_quartets": len(result["orientation_trace"]),
            "generated_orientation_modes": ORIENTATION_MODES,
            "binary_mode_count": BINARY_MODE_COUNT,
            "mode_capacity": MODE_CAPACITY,
            "constitutional_objectives": 9,
            "charge_census": CHARGE_CENSUS,
            "steric_census": STERIC_CENSUS,
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
    print(json.dumps(run_protocol_v10(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
