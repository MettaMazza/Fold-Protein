#!/usr/bin/env python3
"""Run and immutably seal multiscale reconciliation selector V28."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v28 import select_state_path_v28
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _registered_lineage(manifest, v27_run_id, sequence):
    binding = manifest.get("parent_records", {}).get(v27_run_id)
    pairs = (
        ("v25_path", "v25_sha256"),
        ("v26_1_path", "v26_1_sha256"),
        ("v27_path", "v27_sha256"),
        ("domain_path", "domain_sha256"),
    )
    if not isinstance(binding, dict) or set(binding) != {
            item for pair in pairs for item in pair}:
        raise RuntimeError("V28 branch lineage is not registered")
    records = {}
    for path_key, hash_key in pairs:
        path = ROOT / binding[path_key]
        if not path.is_file() or sha256_file(path) != binding[hash_key]:
            raise RuntimeError("V28 registered branch lineage drifted")
        records[path_key] = json.loads(path.read_text())
    v25, v261, v27, domain = (records[key] for key in (
        "v25_path", "v26_1_path", "v27_path", "domain_path"))
    if (v27.get("schema") != "fold-protein-selected-states/v27"
            or v27.get("run_id") != v27_run_id
            or v27.get("sequence") != sequence):
        raise RuntimeError("V28 V27 identity did not close")
    if (v25.get("schema") != "fold-protein-selected-states/v25"
            or v25.get("run_id") != v27.get("v25_run_id")
            or v25.get("sequence") != sequence):
        raise RuntimeError("V28 V25 identity did not close")
    if (v261.get("schema") != "fold-protein-selected-states/v26.1"
            or v261.get("run_id") != v27.get("v26_1_run_id")
            or v261.get("sequence") != sequence):
        raise RuntimeError("V28 V26.1 identity did not close")
    if (domain.get("schema") != "fold-protein-selected-states/v23.2"
            or domain.get("run_id") != v27.get("domain_run_id")
            or domain.get("sequence") != sequence):
        raise RuntimeError("V28 domain identity did not close")
    return v25, v261, v27, domain, binding


def run_protocol_v28(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v28":
        raise ValueError("unsupported selector-v28 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V28 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    v25, v261, v27, domain, binding = _registered_lineage(
        manifest, selector_input["parent_run_id"], sequence)
    expected_config = {
        "base_segment_residues": 4,
        "scale_progression": "repeated doubling through complete chain",
        "branch_sources": ["V25", "V26.1", "V27"],
        "block_transition": "unchanged plus complete branch grafts plus both boundary domains",
        "domain_capacity": 24,
        "frontier_capacity": 24,
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None, "continuity_lock": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v28 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-v28-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v28(
            sequence, v25["states"], v261["states"], v27["states"],
            domain["domain_trace"])
        record = {
            "schema": "fold-protein-selected-states/v28", "status": "completed",
            "run_id": selector_input["run_id"], "sequence": sequence,
            "v25_run_id": v25["run_id"], "v25_sha256": binding["v25_sha256"],
            "v26_1_run_id": v261["run_id"],
            "v26_1_sha256": binding["v26_1_sha256"],
            "v27_run_id": v27["run_id"], "v27_sha256": binding["v27_sha256"],
            "domain_run_id": domain["run_id"],
            "domain_sha256": binding["domain_sha256"],
        }
        for key, value in result.items():
            if key != "atoms":
                record[key] = value
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v28", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "multiscale constitutional branch propagation",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "v25_run_id": v25["run_id"], "v25_sha256": binding["v25_sha256"],
            "v26_1_run_id": v261["run_id"],
            "v26_1_sha256": binding["v26_1_sha256"],
            "v27_run_id": v27["run_id"], "v27_sha256": binding["v27_sha256"],
            "domain_run_id": domain["run_id"],
            "domain_sha256": binding["domain_sha256"],
            "v25_departures": result["v25_departures"],
            "v26_1_departures": result["v26_1_departures"],
            "v27_departures": result["v27_departures"],
            "scales": result["scales"],
            "complete_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY,
            "frontier_capacity": FRONTIER_CAPACITY,
            "base_segment_residues": SEGMENT_RESIDUES,
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("selector_input", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run_protocol_v28(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
