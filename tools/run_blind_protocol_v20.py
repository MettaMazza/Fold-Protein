#!/usr/bin/env python3
"""Run and immutably seal selector v20 before target comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v7 import BINARY_MODE_COUNT, MODE_CAPACITY, MODE_NAMES
from tools.blind_24_lattice_selector_v20 import (
    CHARGE_CENSUS, CONSTITUTIONAL_OBJECTIVES, HARD_EXCLUSION_STRATA,
    HYDROGEN_BOND_CENSUS, SIDECHAIN_GRAPH_SPATIAL_CENSUS, STERIC_CENSUS,
    TOPOLOGY_HYDROGEN_BOND_CENSUS, select_state_path_v20)
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_protocol_v20(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = (
        manifest_path.resolve(), input_path.resolve(), output_dir.resolve())
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v20":
        raise ValueError("unsupported selector-v20 manifest")
    for relative, expected_hash in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise RuntimeError(f"protocol source drift: {relative}")
    input_raw = input_path.read_bytes()
    selector_input = json.loads(input_raw)
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("selector-v20 input must contain run_id and sequence")
    expected = {
        "beam_width": 24,
        "binary_mode_count": BINARY_MODE_COUNT,
        "mode_capacity": MODE_CAPACITY,
        "orientation_residues": 4,
        "generated_modes": list(MODE_NAMES),
        "constitutional_objectives": CONSTITUTIONAL_OBJECTIVES,
        "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        "sidechain_graphs": 20,
        "local_graph_pruning": False,
        "graph_exclusion_fold_denominator": 2,
        "spatial_non_neighbour_separation": 2,
        "spatial_hard_exclusion_unit": "excluded_residue_pair",
        "graph_encounter_child_unit": "explicit_atom_encounter",
    }
    if manifest.get("selector_config") != expected:
        raise RuntimeError("selector-v20 configuration is not the forced census")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-v20-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v20(selector_input["sequence"])
        state_record = {
            "schema": "fold-protein-selected-states/v20",
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
            "hydrogen_bond_census": result["hydrogen_bond_census"],
            "topology_hydrogen_bond_census": result["topology_hydrogen_bond_census"],
            "sidechain_graph_spatial_census": result["sidechain_graph_spatial_census"],
            "hard_exclusion_strata": result["hard_exclusion_strata"],
            "local_graph_pruning": result["local_graph_pruning"],
            "status": "completed",
        }
        state_bytes = (json.dumps(
            state_record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v20",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": (
                "v13 local frontier with hierarchical backbone, graph-pair, "
                "and graph-atom complete-prefix exclusions"),
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(selector_input["sequence"].upper().encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "orientation_quartets": len(result["orientation_trace"]),
            "binary_mode_count": BINARY_MODE_COUNT,
            "mode_capacity": MODE_CAPACITY,
            "constitutional_objectives": CONSTITUTIONAL_OBJECTIVES,
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "local_graph_pruning": False,
            "charge_census": CHARGE_CENSUS,
            "steric_census": STERIC_CENSUS,
            "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
            "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
            "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
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
    print(json.dumps(run_protocol_v20(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
