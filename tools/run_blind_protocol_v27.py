#!/usr/bin/env python3
"""Run and immutably seal branch-reconciliation selector V27."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v27 import select_state_path_v27
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _registered_branches(manifest, v25_run_id, sequence):
    binding = manifest.get("parent_records", {}).get(v25_run_id)
    required = {
        "v25_path", "v25_sha256", "v26_1_path", "v26_1_sha256",
        "domain_path", "domain_sha256"}
    if not isinstance(binding, dict) or set(binding) != required:
        raise RuntimeError("V27 branch lineage is not registered")
    paths = {key: ROOT / binding[key] for key in (
        "v25_path", "v26_1_path", "domain_path")}
    for path_key, hash_key in (("v25_path", "v25_sha256"),
                               ("v26_1_path", "v26_1_sha256"),
                               ("domain_path", "domain_sha256")):
        if (not paths[path_key].is_file()
                or sha256_file(paths[path_key]) != binding[hash_key]):
            raise RuntimeError("V27 registered branch lineage drifted")
    v25 = json.loads(paths["v25_path"].read_text())
    v261 = json.loads(paths["v26_1_path"].read_text())
    domain = json.loads(paths["domain_path"].read_text())
    if (v25.get("schema") != "fold-protein-selected-states/v25"
            or v25.get("run_id") != v25_run_id
            or v25.get("sequence") != sequence):
        raise RuntimeError("V27 V25 identity did not close")
    if (v261.get("schema") != "fold-protein-selected-states/v26.1"
            or v261.get("parent_run_id") != v25_run_id
            or v261.get("sequence") != sequence):
        raise RuntimeError("V27 V26.1 identity did not close")
    if (domain.get("schema") != "fold-protein-selected-states/v23.2"
            or domain.get("run_id") != v25.get("parent_run_id")
            or domain.get("sequence") != sequence):
        raise RuntimeError("V27 local-domain identity did not close")
    return v25, v261, domain, binding


def run_protocol_v27(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v27":
        raise ValueError("unsupported selector-v27 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V27 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    v25, v261, domain, binding = _registered_branches(
        manifest, selector_input["parent_run_id"], sequence)
    expected_config = {
        "branch_domain": "complete binary cube of V25/V26.1 disagreements",
        "branch_cube_capacity": 576, "domain_capacity": 24,
        "frontier_capacity": 24, "segment_residues": 4,
        "continuation": "locally admitted one-coordinate transitions",
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v27 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v27-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v27(
            sequence, v25["states"], v261["states"], domain["domain_trace"])
        record = {
            "schema": "fold-protein-selected-states/v27", "status": "completed",
            "run_id": selector_input["run_id"], "sequence": sequence,
            "v25_run_id": v25["run_id"], "v25_sha256": binding["v25_sha256"],
            "v26_1_run_id": v261["run_id"],
            "v26_1_sha256": binding["v26_1_sha256"],
            "domain_run_id": domain["run_id"],
            "domain_sha256": binding["domain_sha256"],
            "states": result["states"],
            "v25_states": result["v25_states"],
            "v26_1_states": result["v26_1_states"],
            "v25_departures": result["v25_departures"],
            "v26_1_departures": result["v26_1_departures"],
            "branch_cube": result["branch_cube"],
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
            "schema": "fold-protein-blind-seal/v27", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "constitutional V25/V26.1 branch reconciliation",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "v25_run_id": v25["run_id"], "v25_sha256": binding["v25_sha256"],
            "v26_1_run_id": v261["run_id"],
            "v26_1_sha256": binding["v26_1_sha256"],
            "domain_run_id": domain["run_id"],
            "domain_sha256": binding["domain_sha256"],
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "v25_departures": result["v25_departures"],
            "v26_1_departures": result["v26_1_departures"],
            "branch_difference_count": result["branch_cube"]["binary_dimension"],
            "branch_cube_candidates": result["branch_cube"]["complete_candidate_count"],
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
    a = p.parse_args(); print(json.dumps(run_protocol_v27(
        a.manifest, a.selector_input, a.output_dir), sort_keys=True))


if __name__ == "__main__": main()
