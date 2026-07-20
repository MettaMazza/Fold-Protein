#!/usr/bin/env python3
"""Run and immutably seal tertiary segment-body selector V29."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v29 import select_state_path_v29
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def _registered_lineage(manifest, v28_run_id, sequence):
    binding = manifest.get("parent_records", {}).get(v28_run_id)
    pairs = tuple((name + "_path", name + "_sha256") for name in (
        "v25", "v26_1", "v27", "v28", "domain"))
    if not isinstance(binding, dict) or set(binding) != {
            value for pair in pairs for value in pair}:
        raise RuntimeError("V29 branch lineage is not registered")
    records = {}
    for path_key, hash_key in pairs:
        path = ROOT / binding[path_key]
        if not path.is_file() or sha256_file(path) != binding[hash_key]:
            raise RuntimeError("V29 registered branch lineage drifted")
        records[path_key] = json.loads(path.read_text())
    v25, v261, v27, v28, domain = (records[name + "_path"] for name in (
        "v25", "v26_1", "v27", "v28", "domain"))
    expected = (
        (v25, "fold-protein-selected-states/v25", v28["v25_run_id"]),
        (v261, "fold-protein-selected-states/v26.1", v28["v26_1_run_id"]),
        (v27, "fold-protein-selected-states/v27", v28["v27_run_id"]),
        (v28, "fold-protein-selected-states/v28", v28_run_id),
        (domain, "fold-protein-selected-states/v23.2", v28["domain_run_id"]),
    )
    if any(record.get("schema") != schema or record.get("run_id") != run_id
           or record.get("sequence") != sequence
           for record, schema, run_id in expected):
        raise RuntimeError("V29 registered identity did not close")
    return v25, v261, v27, v28, domain, binding


def run_protocol_v29(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v29":
        raise ValueError("unsupported selector-v29 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V29 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    v25, v261, v27, v28, domain, binding = _registered_lineage(
        manifest, selector_input["parent_run_id"], sequence)
    expected_config = {
        "body_residues": 4,
        "topology": "sequence-only ordinal spanning tree",
        "branch_sources": ["V25", "V26.1", "V27", "V28"],
        "edge_transition": "complete ordered body grafts plus all boundary states plus coordinated paired boundaries",
        "domain_capacity": 24, "frontier_capacity": 24,
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None, "continuity_lock": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v29 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-v29-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v29(
            sequence, v25["states"], v261["states"], v27["states"],
            v28["states"], domain["domain_trace"])
        record = {
            "schema": "fold-protein-selected-states/v29", "status": "completed",
            "run_id": selector_input["run_id"], "sequence": sequence,
        }
        for name, source in (("v25", v25), ("v26_1", v261),
                             ("v27", v27), ("v28", v28), ("domain", domain)):
            record[name + "_run_id"] = source["run_id"]
            record[name + "_sha256"] = binding[name + "_sha256"]
        for key, value in result.items():
            if key != "atoms":
                record[key] = value
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v29", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "joint tertiary segment-body topology assembly",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "tree_edge_count": result["tertiary_census"]["tree_edge_count"],
            "complete_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY,
            "frontier_capacity": FRONTIER_CAPACITY,
            "body_residues": SEGMENT_RESIDUES,
            "whole_chain_evaluations": result["whole_chain_evaluations"],
            "runtime_seconds": result["runtime_seconds"],
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        }
        for name, source in (("v25", v25), ("v26_1", v261),
                             ("v27", v27), ("v28", v28), ("domain", domain)):
            seal[name + "_run_id"] = source["run_id"]
            seal[name + "_sha256"] = binding[name + "_sha256"]
        for name in ("v25", "v26_1", "v27", "v28"):
            seal[name + "_departures"] = result[name + "_departures"]
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
    print(json.dumps(run_protocol_v29(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
