#!/usr/bin/env python3
"""Verify the paired V34/V35 panel without opening comparison targets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.run_blind_panel_v35 import (
    ROOT, SELECTOR_ORDER, sha256_file, validate_registration)
from verify.evaluate_sealed_blind_v34 import verify_v34_seal
from verify.evaluate_sealed_blind_v35 import verify_v35_seal


VERIFIERS = {"v34": verify_v34_seal, "v35": verify_v35_seal}


def verify_panel(directory: Path) -> dict:
    directory = directory.resolve()
    registration_path = directory / "panel_registration.json"
    seal_path = directory / "panel_seal.json"
    registration = json.loads(registration_path.read_text())
    proteins = validate_registration(registration)
    seal = json.loads(seal_path.read_text())
    if (seal.get("schema") != "fold-protein-v34-v35-paired-panel-seal/v1"
            or seal.get("status") != "completed"
            or seal.get("official_run") is not False):
        raise RuntimeError("invalid V35 paired panel seal")
    if seal.get("panel_registration_sha256") != sha256_file(registration_path):
        raise RuntimeError("V35 panel registration hash mismatch")

    expected = {
        (protein["protein_id"], version)
        for protein in proteins for version in SELECTOR_ORDER
    }
    rows = {
        (row["protein_id"], row["selector_version"]): row
        for row in seal["runs"]
    }
    if set(rows) != expected or seal.get("prediction_count") != len(expected):
        raise RuntimeError("V35 paired panel coverage mismatch")

    verified = []
    for protein in proteins:
        for version in SELECTOR_ORDER:
            row = rows[(protein["protein_id"], version)]
            nested_dir = directory / protein["protein_id"] / version
            selector = registration["selectors"][version]
            nested_seal, states = VERIFIERS[version](
                ROOT / selector["manifest"], nested_dir)
            checks = {
                "run_id": nested_seal["run_id"],
                "sequence_sha256": nested_seal["sequence_sha256"],
                "selector_input_sha256": nested_seal["selector_input_sha256"],
                "selector_manifest_sha256": nested_seal["protocol_manifest_sha256"],
                "nested_seal_sha256": sha256_file(nested_dir / "seal.json"),
                "selected_states_sha256": nested_seal["selected_states_sha256"],
                "prediction_pdb_sha256": nested_seal["prediction_pdb_sha256"],
            }
            for field, actual in checks.items():
                if row.get(field) != actual:
                    raise RuntimeError(
                        f"V35 panel binding mismatch: {protein['protein_id']} {version} {field}")
            if states["sequence"] != protein["sequence"]:
                raise RuntimeError("V35 panel sequence identity mismatch")
            verified.append({
                "protein_id": protein["protein_id"],
                "selector_version": version,
                "path_length": len(states["states"]),
                "prediction_pdb_sha256": nested_seal["prediction_pdb_sha256"],
            })
    return {
        "schema": "fold-protein-v34-v35-paired-panel-verification/v1",
        "status": "verified",
        "panel_id": seal["panel_id"],
        "panel_registration_sha256": sha256_file(registration_path),
        "panel_seal_sha256": sha256_file(seal_path),
        "verified_predictions": len(verified),
        "runs": verified,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_panel(args.directory), sort_keys=True))


if __name__ == "__main__":
    main()
