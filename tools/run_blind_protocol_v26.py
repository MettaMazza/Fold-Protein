#!/usr/bin/env python3
"""Run and immutably seal joint-topology selector V26."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v26 import TOPOLOGY_CAPACITY, select_state_path_v26
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _registered_lineage(manifest, parent_run_id, sequence):
    binding = manifest.get("parent_records", {}).get(parent_run_id)
    required = {"path", "sha256", "domain_path", "domain_sha256"}
    if not isinstance(binding, dict) or set(binding) != required:
        raise RuntimeError("V26 parent lineage is not registered")
    parent_path, domain_path = ROOT / binding["path"], ROOT / binding["domain_path"]
    if (not parent_path.is_file() or sha256_file(parent_path) != binding["sha256"]
            or not domain_path.is_file()
            or sha256_file(domain_path) != binding["domain_sha256"]):
        raise RuntimeError("V26 registered lineage drifted")
    parent, domain = json.loads(parent_path.read_text()), json.loads(domain_path.read_text())
    if (parent.get("schema") != "fold-protein-selected-states/v25"
            or parent.get("run_id") != parent_run_id
            or parent.get("sequence") != sequence):
        raise RuntimeError("V26 V25 parent identity did not close")
    if (domain.get("schema") != "fold-protein-selected-states/v23.2"
            or domain.get("run_id") != parent.get("parent_run_id")
            or domain.get("sequence") != sequence):
        raise RuntimeError("V26 local-domain lineage did not close")
    return parent, domain, binding


def run_protocol_v26(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v26":
        raise ValueError("unsupported selector-v26 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V26 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    parent, domain, binding = _registered_lineage(
        manifest, selector_input["parent_run_id"], sequence)
    expected_config = {
        "paired_domain_states": 576, "domain_capacity": 24,
        "topology_capacity": 24, "frontier_capacity": 24,
        "segment_residues": 4,
        "topology_selection": "weight-free ordinal unresolved segment relations",
        "paired_transition": "all 24x24 admitted states for every participating residue pair",
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v26 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v26-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v26(
            sequence, parent["states"], domain["domain_trace"])
        record = {
            "schema": "fold-protein-selected-states/v26", "status": "completed",
            "run_id": selector_input["run_id"], "sequence": sequence,
            "parent_run_id": selector_input["parent_run_id"],
            "parent_selected_states_sha256": binding["sha256"],
            "domain_run_id": domain["run_id"],
            "domain_selected_states_sha256": binding["domain_sha256"],
            "states": result["states"], "seed_states": result["seed_states"],
            "parent_departures": result["parent_departures"],
            "topology_pairs": result["topology_pairs"],
            "topology_trace": result["topology_trace"],
            "assembly_trace": result["assembly_trace"],
            "reconciliation": result["reconciliation"],
            "parent_constraint_graph": result["parent_constraint_graph"],
            "final_relations": result["final_relations"],
            "constraint_graph_census": result["constraint_graph_census"],
            "domain_state_count": result["domain_state_count"],
            "domain_capacity": result["domain_capacity"],
            "topology_capacity": result["topology_capacity"],
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
            "schema": "fold-protein-blind-seal/v26", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "joint long-range topology over parent-anchored coordinate basis",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "parent_run_id": selector_input["parent_run_id"],
            "parent_selected_states_sha256": binding["sha256"],
            "domain_run_id": domain["run_id"],
            "domain_selected_states_sha256": binding["domain_sha256"],
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "parent_departures": result["parent_departures"],
            "paired_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY,
            "topology_capacity": TOPOLOGY_CAPACITY,
            "topology_pair_count": len(result["topology_pairs"]),
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
    a = p.parse_args(); print(json.dumps(run_protocol_v26(
        a.manifest, a.selector_input, a.output_dir), sort_keys=True))


if __name__ == "__main__": main()
