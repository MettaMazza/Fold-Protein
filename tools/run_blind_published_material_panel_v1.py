#!/usr/bin/env python3
"""Seal the unchanged published material path on untouched structures."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verify/ubiquitin_24_lattice_manifest.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def encoded(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def run(registration_path: Path, output_dir: Path) -> dict:
    registration_path, output_dir = map(
        Path.resolve, (registration_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(output_dir)
    raw = registration_path.read_bytes()
    registration = json.loads(raw)
    runtime = Path(__file__).resolve()
    if (registration.get("schema")
            != "fold-protein-blind-published-material-panel/v1"
            or registration.get("blind_prediction") is not True
            or registration.get("target_accesses_before_seal") != 0
            or registration.get("runtime_sha256") != digest(runtime)
            or registration.get("published_manifest_sha256")
            != digest(MANIFEST)):
        raise RuntimeError("published blind material registration drifted")
    manifest = json.loads(MANIFEST.read_text())
    sequence = manifest["sequence"]
    states = [int(value) for value in manifest["states"]]
    atoms = build_backbone_coordinates(
        sequence,
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states],
    )
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-published-blind-panel-", dir=output_dir.parent))
    try:
        (stage / "panel_registration.json").write_bytes(raw)
        runs = []
        for protein in registration["proteins"]:
            if protein["sequence"] != sequence:
                raise RuntimeError("registered sequence differs from published path")
            nested = stage / protein["protein_id"]
            nested.mkdir()
            write_pdb(atoms, nested / "prediction.pdb")
            selected = {
                "schema": "fold-protein-blind-published-material-states/v1",
                "status": "completed",
                "blind_prediction": True,
                "protein_id": protein["protein_id"],
                "sequence": sequence,
                "sequence_sha256": sha256(sequence.encode()).hexdigest(),
                "states": states,
                "weights": 0,
                "fitted_parameters": 0,
                "target_accesses": 0,
            }
            selected_raw = encoded(selected)
            (nested / "selected_states.json").write_bytes(selected_raw)
            seal = {
                "schema": "fold-protein-blind-published-material-seal/v1",
                "status": "completed",
                "blind_prediction": True,
                "protein_id": protein["protein_id"],
                "sequence_sha256": selected["sequence_sha256"],
                "selected_states_sha256": sha256(selected_raw).hexdigest(),
                "prediction_pdb_sha256": digest(nested / "prediction.pdb"),
                "runtime_sha256": registration["runtime_sha256"],
                "published_manifest_sha256": registration[
                    "published_manifest_sha256"],
                "target_accesses": 0,
            }
            seal_raw = encoded(seal)
            (nested / "seal.json").write_bytes(seal_raw)
            runs.append({
                "protein_id": protein["protein_id"],
                "sequence_sha256": seal["sequence_sha256"],
                "prediction_pdb_sha256": seal["prediction_pdb_sha256"],
                "selected_states_sha256": seal["selected_states_sha256"],
                "nested_seal_sha256": sha256(seal_raw).hexdigest(),
            })
        panel = {
            "schema": "fold-protein-blind-published-material-panel-seal/v1",
            "status": "completed",
            "result_type": "cumulative blind development benchmark",
            "official_run": False,
            "blind_prediction": True,
            "panel_id": registration["panel_id"],
            "panel_registration_sha256": sha256(raw).hexdigest(),
            "runtime_sha256": registration["runtime_sha256"],
            "published_manifest_sha256": registration[
                "published_manifest_sha256"],
            "prediction_count": len(runs),
            "target_accesses_before_seal": 0,
            "runs": runs,
        }
        (stage / "panel_seal.json").write_bytes(encoded(panel))
        os.replace(stage, output_dir)
        return panel
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("registration", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.registration, args.output_dir), sort_keys=True))
