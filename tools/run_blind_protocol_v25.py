#!/usr/bin/env python3
"""Run and immutably seal parent-anchored coordinate-beam selector V25."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v25 import select_state_path_v25
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _registered_parent(manifest, parent_run_id, sequence):
    binding = manifest.get("parent_records", {}).get(parent_run_id)
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
        raise RuntimeError("V25 parent record is not registered")
    path = ROOT / binding["path"]
    if not path.is_file() or sha256_file(path) != binding["sha256"]:
        raise RuntimeError("V25 registered V23.2 parent drifted")
    record = json.loads(path.read_text())
    if (record.get("schema") != "fold-protein-selected-states/v23.2"
            or record.get("run_id") != parent_run_id
            or record.get("sequence") != sequence):
        raise RuntimeError("V25 parent identity did not close")
    return record, binding


def run_protocol_v25(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v25":
        raise ValueError("unsupported selector-v25 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V25 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    parent, parent_binding = _registered_parent(
        manifest, selector_input["parent_run_id"], sequence)
    expected_config = {
        "complete_domain_states": 576, "domain_capacity": 24,
        "segment_residues": 4, "frontier_capacity": 24,
        "move_basis": "unchanged path plus every admitted one-coordinate transition per segment",
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v25 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v25-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v25(
            sequence, parent["states"], parent["domain_trace"])
        record = {
            "schema": "fold-protein-selected-states/v25", "status": "completed",
            "run_id": selector_input["run_id"], "sequence": sequence,
            "parent_run_id": selector_input["parent_run_id"],
            "parent_selected_states_sha256": parent_binding["sha256"],
            "states": result["states"], "seed_states": result["seed_states"],
            "parent_departures": result["parent_departures"],
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
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v25", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "parent-anchored bidirectional constitutional coordinate beam",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "parent_run_id": selector_input["parent_run_id"],
            "parent_selected_states_sha256": parent_binding["sha256"],
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "parent_departures": result["parent_departures"],
            "complete_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY,
            "frontier_capacity": FRONTIER_CAPACITY,
            "segment_residues": SEGMENT_RESIDUES,
            "segment_count": result["segment_count"],
            "whole_chain_evaluations": result["whole_chain_evaluations"],
            "runtime_seconds": result["runtime_seconds"],
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        }
        (stage / "seal.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
        os.replace(stage, output_dir)
        return seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main():
    p = argparse.ArgumentParser(); p.add_argument("manifest", type=Path)
    p.add_argument("selector_input", type=Path); p.add_argument("output_dir", type=Path)
    a = p.parse_args(); print(json.dumps(run_protocol_v25(
        a.manifest, a.selector_input, a.output_dir), sort_keys=True))


if __name__ == "__main__": main()
