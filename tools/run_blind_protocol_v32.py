#!/usr/bin/env python3
"""Run and immutably seal cross-topology consensus selector V32."""
from __future__ import annotations

import argparse, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, SEGMENT_RESIDUES)
from tools.blind_24_lattice_selector_v32 import select_state_path_v32
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes, sha256_file
from tools.run_blind_protocol_v29 import _registered_lineage
from tools.tertiary_segment_body_constitution_v3 import DEGREE_FRONTIER

ROOT = Path(__file__).resolve().parents[1]


def _registered_v32_lineage(manifest, parent_id, sequence):
    binding = manifest.get("parent_records", {}).get(parent_id)
    if not isinstance(binding, dict):
        raise RuntimeError("V32 topology lineage is not registered")
    v29_manifest = json.loads((ROOT / "verify/blind_selector_v29.json").read_text())
    v25, v261, v27, v28, domain, base_binding = _registered_lineage(
        v29_manifest, binding["v28_run_id"], sequence)
    records = {}
    for name in ("v29", "v30"):
        path = ROOT / binding[name + "_path"]
        if sha256_file(path) != binding[name + "_sha256"]:
            raise RuntimeError(f"V32 registered {name} branch drifted")
        record = json.loads(path.read_text())
        if (record.get("schema") != f"fold-protein-selected-states/{name}"
                or record.get("run_id") != binding[name + "_run_id"]
                or record.get("sequence") != sequence):
            raise RuntimeError(f"V32 registered {name} identity did not close")
        records[name] = record
    return v25, v261, v27, v28, records["v29"], records["v30"], domain, binding, base_binding


def run_protocol_v32(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(
        Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v32":
        raise ValueError("unsupported selector-v32 manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise ValueError("V32 input must contain run_id, sequence, parent_run_id")
    sequence = selector_input["sequence"].upper()
    lineage = _registered_v32_lineage(
        manifest, selector_input["parent_run_id"], sequence)
    v25, v261, v27, v28, v29, v30, domain, binding, base_binding = lineage
    expected_config = {
        "body_residues": 4, "degree_frontier": [2, 3, 4],
        "topology": "complete counted bounded-degree ordinal frontier",
        "consensus": "minimum counted state distance to every topology family",
        "branch_sources": ["V25", "V26.1", "V27", "V28", "V29", "V30"],
        "domain_capacity": 24, "frontier_capacity": 24,
        "assembly_directions": ["forward", "reverse"],
        "target": None, "template": None, "reward": None,
        "weight": None, "trained_parameter": None, "continuity_lock": None,
    }
    if (manifest.get("selector_config") != expected_config
            or tuple(manifest["selector_config"]["degree_frontier"]) != DEGREE_FRONTIER):
        raise RuntimeError("selector-v32 configuration drift")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v32-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path_v32(
            sequence, v25["states"], v261["states"], v27["states"],
            v28["states"], v29["states"], v30["states"], domain["domain_trace"])
        sources = {"v25": v25, "v26_1": v261, "v27": v27, "v28": v28,
                   "v29": v29, "v30": v30, "domain": domain}
        record = {"schema": "fold-protein-selected-states/v32",
                  "status": "completed", "run_id": selector_input["run_id"],
                  "sequence": sequence}
        for name, source in sources.items():
            record[name + "_run_id"] = source["run_id"]
            record[name + "_sha256"] = (binding[name + "_sha256"]
                                          if name in ("v29", "v30")
                                          else base_binding[name + "_sha256"])
        record.update({key: value for key, value in result.items() if key != "atoms"})
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v32", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "constitutional cross-topology consensus",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]), "degree_frontier": list(DEGREE_FRONTIER),
            "consensus_candidate_count": result["consensus"]["candidate_count"],
            "consensus_retained_paths": result["consensus"]["retained_paths"],
            "complete_domain_states": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY, "frontier_capacity": FRONTIER_CAPACITY,
            "body_residues": SEGMENT_RESIDUES,
            "whole_chain_evaluations": result["whole_chain_evaluations"],
            "runtime_seconds": result["runtime_seconds"],
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        }
        for name, source in sources.items():
            seal[name + "_run_id"] = source["run_id"]
            seal[name + "_sha256"] = record[name + "_sha256"]
        for name in ("v25", "v26_1", "v27", "v28", "v29", "v30"):
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
    print(json.dumps(run_protocol_v32(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
