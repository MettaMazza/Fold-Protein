#!/usr/bin/env python3
"""Seal a target-inaccessible One-extension panel from the published path.

The runtime accepts only registered sequences consisting of the frozen
ubiquitin material sequence followed by exactly One terminal residue.  It
preserves the complete published 76-state path and applies the canonical
C-terminal psi gauge to the One advance.  No experimental target, score,
target-derived multi-protein witness, alignment model or fitted quantity is
read or imported.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verify/ubiquitin_24_lattice_manifest.json"
SCHEMA = "fold-protein-blind-material-one-extension-panel/v1"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def extension_path(sequence: str, manifest: dict) -> list[int]:
    template = manifest["sequence"]
    if len(sequence) != len(template) + 1 or not sequence.startswith(template):
        raise RuntimeError("sequence is not the exact theorem-forced One extension")
    states = [int(value) for value in manifest["states"]]
    if len(states) != len(template) or states[-1] != 0:
        raise RuntimeError("published material path or terminal gauge drifted")
    # The prior terminal state becomes interior without alteration.  The new
    # terminal residue receives the same exact canonical terminal gauge state.
    return states + [0]


def run(registration_path: Path, output_dir: Path) -> dict:
    registration_path = registration_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)
    raw = registration_path.read_bytes()
    registration = json.loads(raw)
    if (registration.get("schema") != SCHEMA
            or registration.get("official_run") is not False
            or registration.get("blind_prediction") is not True
            or registration.get("target_accesses_before_seal") != 0):
        raise RuntimeError("blind One-extension registration drifted")
    if file_sha256(MANIFEST) != registration["published_manifest_sha256"]:
        raise RuntimeError("published material manifest drifted")
    runtime = Path(__file__).resolve()
    if file_sha256(runtime) != registration["runtime_sha256"]:
        raise RuntimeError("blind runtime drifted")
    manifest = json.loads(MANIFEST.read_text())

    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-blind-one-extension-", dir=output_dir.parent))
    try:
        (stage / "panel_registration.json").write_bytes(raw)
        runs = []
        for protein in registration["proteins"]:
            sequence = protein["sequence"]
            states = extension_path(sequence, manifest)
            phi = [angles_for_state(state)[0] for state in states]
            psi = [angles_for_state(state)[1] for state in states]
            started = time.perf_counter()
            atoms = build_backbone_coordinates(sequence, phi, psi)
            nested = stage / protein["protein_id"]
            nested.mkdir()
            write_pdb(atoms, nested / "prediction.pdb")
            selected = {
                "schema": "fold-protein-blind-material-one-extension-states/v1",
                "status": "completed",
                "result_type": "cumulative blind development benchmark",
                "official_run": False,
                "blind_prediction": True,
                "protein_id": protein["protein_id"],
                "sequence": sequence,
                "sequence_sha256": sha256(sequence.encode()).hexdigest(),
                "states": states,
                "relation": "published material path followed by One terminal advance",
                "weights": 0,
                "fitted_parameters": 0,
                "target_accesses": 0,
                "elapsed_seconds": time.perf_counter() - started,
            }
            selected_raw = json_bytes(selected)
            (nested / "selected_states.json").write_bytes(selected_raw)
            seal = {
                "schema": "fold-protein-blind-material-one-extension-seal/v1",
                "status": "completed",
                "blind_prediction": True,
                "protein_id": protein["protein_id"],
                "sequence_sha256": selected["sequence_sha256"],
                "selected_states_sha256": sha256(selected_raw).hexdigest(),
                "prediction_pdb_sha256": file_sha256(nested / "prediction.pdb"),
                "published_manifest_sha256": registration[
                    "published_manifest_sha256"],
                "runtime_sha256": registration["runtime_sha256"],
                "weights": 0,
                "fitted_parameters": 0,
                "target_accesses": 0,
            }
            seal_raw = json_bytes(seal)
            (nested / "seal.json").write_bytes(seal_raw)
            runs.append({
                "protein_id": protein["protein_id"],
                "sequence_sha256": seal["sequence_sha256"],
                "selected_states_sha256": seal["selected_states_sha256"],
                "prediction_pdb_sha256": seal["prediction_pdb_sha256"],
                "nested_seal_sha256": sha256(seal_raw).hexdigest(),
            })
        panel_seal = {
            "schema": "fold-protein-blind-material-one-extension-panel-seal/v1",
            "status": "completed",
            "result_type": "cumulative blind development benchmark",
            "official_run": False,
            "blind_prediction": True,
            "panel_id": registration["panel_id"],
            "panel_registration_sha256": sha256(raw).hexdigest(),
            "published_manifest_sha256": registration[
                "published_manifest_sha256"],
            "runtime_sha256": registration["runtime_sha256"],
            "prediction_count": len(runs),
            "target_accesses_before_seal": 0,
            "runs": runs,
        }
        (stage / "panel_seal.json").write_bytes(json_bytes(panel_seal))
        os.replace(stage, output_dir)
        return panel_seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("registration", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.registration, args.output_dir), sort_keys=True))
