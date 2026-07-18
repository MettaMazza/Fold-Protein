#!/usr/bin/env python3
"""Verify a sealed selector-v2 diagnostic panel and all nested prediction seals."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_panel(directory: Path) -> dict:
    directory = directory.resolve()
    registration_path = directory / "panel_registration.json"
    panel_seal_path = directory / "panel_seal.json"
    registration = json.loads(registration_path.read_text())
    panel_seal = json.loads(panel_seal_path.read_text())
    if panel_seal.get("panel_registration_sha256") != sha256(registration_path):
        raise RuntimeError("panel registration hash mismatch")
    if panel_seal.get("status") != "completed":
        raise RuntimeError("panel is not completed")
    registered = {row["run_id"]: row for row in registration["sequences"]}
    bound = {row["run_id"]: row for row in panel_seal["runs"]}
    if set(registered) != set(bound):
        raise RuntimeError("panel run coverage differs from registration")
    for run_id, binding in bound.items():
        run_dir = directory / run_id
        seal_path = run_dir / "seal.json"
        if sha256(seal_path) != binding["seal_sha256"]:
            raise RuntimeError(f"nested seal hash mismatch: {run_id}")
        seal = json.loads(seal_path.read_text())
        if sha256(run_dir / "selected_states.json") != seal["selected_states_sha256"]:
            raise RuntimeError(f"selected-state hash mismatch: {run_id}")
        if sha256(run_dir / "prediction.pdb") != seal["prediction_pdb_sha256"]:
            raise RuntimeError(f"prediction hash mismatch: {run_id}")
        if seal["selected_states_sha256"] != binding["selected_states_sha256"] or \
                seal["prediction_pdb_sha256"] != binding["prediction_pdb_sha256"]:
            raise RuntimeError(f"panel binding differs from nested seal: {run_id}")
    return {
        "schema": "fold-protein-selector-v2-panel-verification/v1",
        "status": "verified",
        "verified_runs": len(bound),
        "panel_registration_sha256": sha256(registration_path),
        "panel_seal_sha256": sha256(panel_seal_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_panel(args.directory), sort_keys=True))


if __name__ == "__main__":
    main()
