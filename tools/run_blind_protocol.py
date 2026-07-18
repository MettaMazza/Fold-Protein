#!/usr/bin/env python3
"""Run and seal a target-isolated Fold Protein development prediction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

try:
    from tools.blind_24_lattice_solver import SelectorConfig, select_state_path
    from tools.predict_structure import write_pdb
except ImportError:
    from blind_24_lattice_solver import SelectorConfig, select_state_path
    from predict_structure import write_pdb


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_INPUT_FIELDS = {"run_id", "sequence"}
PROHIBITED_WORDS = {"target", "native", "reference", "template", "distance_map", "pdb"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _check_source_hashes(manifest: dict) -> None:
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"protocol source drift: {relative}")


def _load_input(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or set(data) != ALLOWED_INPUT_FIELDS:
        extras = sorted(set(data) - ALLOWED_INPUT_FIELDS) if isinstance(data, dict) else []
        raise ValueError(f"selector input must contain only run_id and sequence; extras={extras}")
    lowered = " ".join(str(key).lower() for key in data)
    if any(word in lowered for word in PROHIBITED_WORDS):
        raise ValueError("selector input contains a prohibited target capability")
    if not isinstance(data["run_id"], str) or not data["run_id"].strip():
        raise ValueError("run_id must be a non-empty string")
    return data, raw


def run_protocol(manifest_path: Path, input_path: Path, output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"sealed output already exists: {output_dir}")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v1":
        raise ValueError("unsupported selector manifest")
    _check_source_hashes(manifest)
    selector_input, input_raw = _load_input(input_path)
    config = SelectorConfig(**manifest["selector_config"])

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_path(selector_input["sequence"], config)
        state_record = {
            "schema": "fold-protein-selected-states/v1",
            "run_id": selector_input["run_id"],
            "sequence": selector_input["sequence"].upper(),
            "states": result["states"],
            "score_trace": result["score_trace"],
            "final_score": result["final_score"],
            "status": "completed",
        }
        state_bytes = (json.dumps(state_record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "selected_states.json").write_bytes(state_bytes)
        write_pdb(result["atoms"], str(stage / "prediction.pdb"))

        seal = {
            "schema": "fold-protein-blind-seal/v1",
            "status": "completed",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256_bytes(manifest_raw),
            "selector_input_sha256": sha256_bytes(input_raw),
            "sequence_sha256": sha256_bytes(selector_input["sequence"].upper().encode()),
            "source_sha256": manifest["source_sha256"],
            "selected_states_sha256": sha256_bytes(state_bytes),
            "prediction_pdb_sha256": sha256_file(stage / "prediction.pdb"),
            "lattice_states": manifest["lattice"]["states"],
            "path_length": len(result["states"]),
        }
        (stage / "seal.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
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
    seal = run_protocol(args.manifest, args.selector_input, args.output_dir)
    print(json.dumps(seal, sort_keys=True))


if __name__ == "__main__":
    main()
