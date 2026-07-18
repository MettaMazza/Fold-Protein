#!/usr/bin/env python3
"""Verify a selector-v2 real-sequence length ladder and every nested seal."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_ladder(directory: Path) -> dict:
    directory = directory.resolve()
    registration_path = directory / "ladder_registration.json"
    seal_path = directory / "ladder_seal.json"
    registration = json.loads(registration_path.read_text())
    seal = json.loads(seal_path.read_text())
    if seal.get("registration_sha256") != sha256(registration_path):
        raise RuntimeError("length-ladder registration hash mismatch")
    expected = registration["lengths"]
    if [row["length"] for row in seal.get("runs", [])] != expected:
        raise RuntimeError("length-ladder coverage/order mismatch")
    sequence = registration["sequence"].upper()
    completed = 0
    failed = 0
    for binding in seal["runs"]:
        length = binding["length"]
        run_id = binding["run_id"]
        execution = directory / f"{run_id}-execution.json"
        if sha256(execution) != binding["execution_sha256"]:
            raise RuntimeError(f"execution receipt mismatch: {run_id}")
        if binding["candidate_count"] != 24 + 24 * 576 * (length - 2):
            raise RuntimeError(f"candidate census mismatch: {run_id}")
        if binding["status"] == "failed":
            failed += 1
            if "error_type" not in binding:
                raise RuntimeError(f"unexplained ladder failure: {run_id}")
            continue
        if binding["status"] != "completed":
            raise RuntimeError(f"unsupported ladder run status: {run_id}")
        completed += 1
        run_dir = directory / run_id
        nested_seal_path = run_dir / "seal.json"
        if sha256(nested_seal_path) != binding["nested_seal_sha256"]:
            raise RuntimeError(f"nested seal mismatch: {run_id}")
        nested = json.loads(nested_seal_path.read_text())
        selector_input = json.loads((run_dir / "selector_input.json").read_text())
        states = json.loads((run_dir / "selected_states.json").read_text())
        if selector_input != {"run_id": run_id, "sequence": sequence[:length]}:
            raise RuntimeError(f"registered prefix mismatch: {run_id}")
        if nested["path_length"] != length or len(states["states"]) != length:
            raise RuntimeError(f"path length mismatch: {run_id}")
        if sha256(run_dir / "selected_states.json") != binding["selected_states_sha256"]:
            raise RuntimeError(f"selected states mismatch: {run_id}")
        if sha256(run_dir / "prediction.pdb") != binding["prediction_pdb_sha256"]:
            raise RuntimeError(f"prediction mismatch: {run_id}")
    expected_status = "completed" if failed == 0 else "completed_with_failures"
    if seal.get("status") != expected_status:
        raise RuntimeError("length-ladder aggregate status mismatch")
    return {
        "schema": "fold-protein-selector-v2-length-ladder-verification/v1",
        "status": "verified",
        "completed_runs": completed,
        "failed_runs": failed,
        "registration_sha256": sha256(registration_path),
        "seal_sha256": sha256(seal_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_ladder(args.directory), sort_keys=True))


if __name__ == "__main__":
    main()
