#!/usr/bin/env python3
"""Run and immutably seal degree-two tertiary path selector V30."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v30 import select_state_path_v30
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file
from tools.run_blind_protocol_v29 import _registered_lineage

ROOT = Path(__file__).resolve().parents[1]


def run_protocol_v30(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v30":
        raise ValueError("unsupported selector-v30 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V30 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    lineage_manifest = json.loads((ROOT / "verify/blind_selector_v29.json").read_text())
    v25, v261, v27, v28, domain, binding = _registered_lineage(
        lineage_manifest, selector_input["parent_run_id"], sequence)
    expected_config = {
        "body_residues": 4, "body_boundary_capacity": 2,
        "topology": "sequence-only ordinal degree-two spanning path",
        "branch_sources": ["V25", "V26.1", "V27", "V28"],
        "edge_transition": "complete ordered body grafts plus all boundary states plus coordinated paired boundaries",
        "domain_capacity": 24, "frontier_capacity": 24,
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None, "continuity_lock": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("selector-v30 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v30-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v30(
            sequence, v25["states"], v261["states"], v27["states"],
            v28["states"], domain["domain_trace"])
        record = {"schema": "fold-protein-selected-states/v30",
                  "status": "completed", "run_id": selector_input["run_id"],
                  "sequence": sequence}
        for name, source in (("v25", v25), ("v26_1", v261),
                             ("v27", v27), ("v28", v28), ("domain", domain)):
            record[name + "_run_id"] = source["run_id"]
            record[name + "_sha256"] = binding[name + "_sha256"]
        record.update({key: value for key, value in result.items() if key != "atoms"})
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v30", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "degree-two tertiary segment-path assembly",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "tertiary_path_edge_count": result["tertiary_census"]["path_edge_count"],
            "complete_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY, "frontier_capacity": FRONTIER_CAPACITY,
            "body_residues": SEGMENT_RESIDUES,
            "body_boundary_capacity": 2,
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
        (stage / "seal.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
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
    print(json.dumps(run_protocol_v30(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
