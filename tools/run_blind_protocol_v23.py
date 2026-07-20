#!/usr/bin/env python3
"""Run and immutably seal selector v23 before target comparison."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v23 import (
    CACHE_CAPACITY, DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES, select_state_path_v23)
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _registered_seed(manifest: dict, seed_run_id: str, sequence: str):
    seed = manifest.get("seed_records", {}).get(seed_run_id)
    if not isinstance(seed, dict) or set(seed) != {"path", "sha256"}:
        raise RuntimeError("v23 seed is not registered by the protocol manifest")
    path = ROOT / seed["path"]
    if not path.is_file() or sha256_file(path) != seed["sha256"]:
        raise RuntimeError("v23 registered seed source drifted")
    record = json.loads(path.read_text())
    if (record.get("schema") != "fold-protein-selected-states/v13"
            or record.get("run_id") != seed_run_id
            or record.get("sequence") != sequence
            or len(record.get("states", [])) != len(sequence)):
        raise RuntimeError("v23 registered V13 seed identity did not close")
    return record, seed


def run_protocol_v23(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path, input_path, output_dir = (
        manifest_path.resolve(), input_path.resolve(), output_dir.resolve())
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v23":
        raise ValueError("unsupported selector-v23 manifest")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    input_raw = input_path.read_bytes()
    selector_input = json.loads(input_raw)
    if set(selector_input) != {"run_id", "sequence", "seed_run_id"}:
        raise ValueError("selector-v23 input must contain run_id, sequence, seed_run_id")
    sequence = str(selector_input["sequence"]).upper()
    seed_record, seed_source = _registered_seed(
        manifest, selector_input["seed_run_id"], sequence)
    expected = {
        "lattice_axis": 24,
        "complete_domain_states": DOMAIN_STATE_COUNT,
        "domain_capacity": DOMAIN_CAPACITY,
        "frontier_capacity": FRONTIER_CAPACITY,
        "cache_capacity": CACHE_CAPACITY,
        "segment_residues": SEGMENT_RESIDUES,
        "assembly_directions": ["forward", "reverse"],
        "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        "local_graph_pruning": False,
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected:
        raise RuntimeError("selector-v23 configuration is not the forced census")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-v23-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v23(sequence, seed_record["states"])
        state_record = {
            "schema": "fold-protein-selected-states/v23",
            "run_id": selector_input["run_id"], "sequence": sequence,
            "seed_run_id": selector_input["seed_run_id"],
            "seed_selected_states_sha256": seed_source["sha256"],
            "states": result["states"], "seed_states": result["seed_states"],
            "domain_trace": result["domain_trace"],
            "assembly_trace": result["assembly_trace"],
            "reconciliation": result["reconciliation"],
            "final_relations": result["final_relations"],
            "constraint_graph_census": result["constraint_graph_census"],
            "domain_state_count": result["domain_state_count"],
            "domain_capacity": result["domain_capacity"],
            "frontier_capacity": result["frontier_capacity"],
            "segment_residues": result["segment_residues"],
            "segment_count": result["segment_count"],
            "whole_chain_evaluations": result["whole_chain_evaluations"],
            "whole_chain_cache_hits": result["whole_chain_cache_hits"],
            "runtime_seconds": result["runtime_seconds"],
            "orientation_modes": result["orientation_modes"],
            "orientation_trace": result["orientation_trace"],
            "charge_census": result["charge_census"],
            "steric_census": result["steric_census"],
            "hydrogen_bond_census": result["hydrogen_bond_census"],
            "topology_hydrogen_bond_census": result["topology_hydrogen_bond_census"],
            "sidechain_graph_spatial_census": result["sidechain_graph_spatial_census"],
            "status": "completed",
        }
        state_bytes = (json.dumps(state_record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v23", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "complete-domain bidirectional global segment assembly",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "seed_run_id": selector_input["seed_run_id"],
            "seed_selected_states_sha256": seed_source["sha256"],
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "complete_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY,
            "frontier_capacity": FRONTIER_CAPACITY,
            "segment_residues": SEGMENT_RESIDUES,
            "segment_count": result["segment_count"],
            "whole_chain_evaluations": result["whole_chain_evaluations"],
            "runtime_seconds": result["runtime_seconds"],
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
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
    print(json.dumps(run_protocol_v23(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
