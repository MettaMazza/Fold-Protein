#!/usr/bin/env python3
"""Run and seal the V34 engine-closed-domain/V3-order composition."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v34 import (
    closed_angle_domain, select_state_path_v34)
from tools.blind_24_lattice_selector_v3 import forced_beam_width
from tools.protein_backbone_geometry_v1 import write_pdb


ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_protocol_v34(manifest_path: Path, input_path: Path,
                     output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw = manifest_path.read_bytes()
    input_raw = input_path.read_bytes()
    manifest = json.loads(manifest_raw)
    selector_input = json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v34":
        raise ValueError("unsupported selector-v34 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise ValueError("V34 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V34 protocol source drift: {relative}")
    expected_config = {
        "beam_width": forced_beam_width(),
        "candidate_domain": closed_angle_domain(),
        "candidate_domain_count": 2,
        "lookahead_residues": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest.get("selector_config") != expected_config:
        raise RuntimeError("V34 selector configuration drift")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v34-sealed-",
                                  dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        sequence = str(selector_input["sequence"]).upper()
        result = select_state_path_v34(sequence)
        record = {
            "schema": "fold-protein-selected-states/v34",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "sequence": sequence,
            "states": result["states"],
            "modes": result["modes"],
            "closed_domain": result["closed_domain"],
            "score_trace": result["score_trace"],
            "final_key": result["final_key"],
        }
        state_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], stage / "prediction.pdb")
        seal = {
            "schema": "fold-protein-blind-seal/v34",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": "V3 ordering over the engine-closed V2 alpha/beta domain",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(sequence.encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "path_length": len(result["states"]),
            "candidate_domain": result["closed_domain"],
            "beam_width": forced_beam_width(),
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
    print(json.dumps(run_protocol_v34(
        args.manifest, args.selector_input, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
