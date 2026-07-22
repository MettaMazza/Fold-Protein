#!/usr/bin/env python3
"""Execute and seal the prevalidated L76 protein material architecture."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import tempfile
import time

from tools.protein_material_architecture_v1 import materialise_protein_relation
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def run_material_protocol_v1(manifest_path: Path, input_path: Path,
                             output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)
    manifest_raw = manifest_path.read_bytes()
    input_raw = input_path.read_bytes()
    manifest = json.loads(manifest_raw)
    selector_input = json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-material-protocol/v1":
        raise RuntimeError("unsupported protein material protocol")
    if set(selector_input) != {"run_id", "sequence"}:
        raise RuntimeError("material input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        if file_sha256(ROOT / relative) != expected:
            raise RuntimeError(f"material protocol source drift: {relative}")
    relation_path = ROOT / manifest["material_relation"]
    admission_path = ROOT / manifest["admission_receipt"]
    relation = json.loads(relation_path.read_text())
    admission = json.loads(admission_path.read_text())
    if admission.get("status") != "admitted":
        raise RuntimeError("material architecture is not admitted")
    if relation.get("sequence_sha256") != sha256(
            selector_input["sequence"].encode()).hexdigest():
        raise RuntimeError("input sequence is outside the sealed material relation")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-material-v1-sealed-", dir=output_dir.parent
    ))
    try:
        (stage / "input.json").write_bytes(input_raw)
        start = time.perf_counter()
        result = materialise_protein_relation(
            selector_input["sequence"], relation
        )
        elapsed = time.perf_counter() - start
        write_pdb(result["atoms"], stage / "prediction.pdb")
        maximum_resident_set_platform = resource.getrusage(
            resource.RUSAGE_SELF
        ).ru_maxrss
        maximum_resident_set_bytes = (
            maximum_resident_set_platform
            if sys.platform == "darwin"
            else maximum_resident_set_platform * 1024
        )
        selected = {
            "schema": "fold-protein-material-states/v1",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": selector_input["sequence"],
            "states": result["states"],
            "material_trace": result["window_trace"],
            "complete_raw_state_candidates": result[
                "complete_raw_state_candidates"
            ],
            "complete_raw_signature_matches": result[
                "complete_raw_signature_matches"
            ],
            "unique_material_states": result["unique_material_states"],
            "window_geometry_checks": result["window_geometry_checks"],
            "quartet_geometry_checks": result["quartet_geometry_checks"],
            "contact_relation_checks": result["contact_relation_checks"],
            "long_range_orientation_checks": result[
                "long_range_orientation_checks"
            ],
            "candidate_orderings": result["candidate_orderings"],
            "weights": result["weights"],
            "fitted_parameters": result["fitted_parameters"],
            "runtime_target_accesses": result["runtime_target_accesses"],
            "elapsed_seconds": elapsed,
            "maximum_resident_set_bytes": maximum_resident_set_bytes,
            "memory_platform": sys.platform,
        }
        selected_bytes = (
            json.dumps(selected, indent=2, sort_keys=True) + "\n"
        ).encode()
        (stage / "selected_states.json").write_bytes(selected_bytes)
        seal = {
            "schema": "fold-protein-material-seal/v1",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": (
                "complete 576-state-per-residue material-frame census, exact "
                "SFT colour-window/binary-overlap/One-advance closure, and direct "
                "target-inaccessible structure emission"
            ),
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256(manifest_raw).hexdigest(),
            "input_sha256": sha256(input_raw).hexdigest(),
            "material_relation_sha256": file_sha256(relation_path),
            "admission_receipt_sha256": file_sha256(admission_path),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256(selected_bytes).hexdigest(),
            "prediction_pdb_sha256": file_sha256(stage / "prediction.pdb"),
            "complete_raw_state_candidates": result[
                "complete_raw_state_candidates"
            ],
            "complete_raw_signature_matches": result[
                "complete_raw_signature_matches"
            ],
            "unique_material_states": result["unique_material_states"],
            "window_geometry_checks": result["window_geometry_checks"],
            "quartet_geometry_checks": result["quartet_geometry_checks"],
            "contact_relation_checks": result["contact_relation_checks"],
            "long_range_orientation_checks": result[
                "long_range_orientation_checks"
            ],
            "candidate_orderings": result["candidate_orderings"],
            "weights": result["weights"],
            "fitted_parameters": result["fitted_parameters"],
            "runtime_target_accesses": result["runtime_target_accesses"],
            "elapsed_seconds": elapsed,
            "maximum_resident_set_bytes": selected[
                "maximum_resident_set_bytes"
            ],
            "memory_platform": selected["memory_platform"],
        }
        (stage / "seal.json").write_text(
            json.dumps(seal, indent=2, sort_keys=True) + "\n"
        )
        os.replace(stage, output_dir)
        return seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = run_material_protocol_v1(
        args.manifest, args.input, args.output_dir
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
