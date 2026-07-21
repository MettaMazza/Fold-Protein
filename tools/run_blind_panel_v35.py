#!/usr/bin/env python3
"""Run and atomically seal the paired V34/V35 multi-protein panel."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

from tools.run_blind_protocol_v34 import run_protocol_v34
from tools.run_blind_protocol_v35 import run_protocol_v35


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "fold-protein-v34-v35-paired-panel/v1"
SELECTOR_ORDER = ("v34", "v35")
RUNNERS = {"v34": run_protocol_v34, "v35": run_protocol_v35}
SELECTOR_SCHEMAS = {
    "v34": "fold-protein-blind-selector/v34",
    "v35": "fold-protein-blind-selector/v35",
}
AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def validate_registration(registration: dict) -> list[dict]:
    expected_keys = {
        "schema", "execution", "result_type", "official_run", "panel_id",
        "runner_source_sha256", "selectors", "proteins",
    }
    if set(registration) != expected_keys or registration["schema"] != SCHEMA:
        raise ValueError("unsupported or incomplete V35 panel registration")
    if registration["result_type"] != "cumulative development benchmark":
        raise ValueError("V35 panel must remain a cumulative development benchmark")
    if registration["official_run"] is not False:
        raise ValueError("only Maria may register an official run")
    if list(registration["selectors"]) != list(SELECTOR_ORDER):
        raise ValueError("paired selector order must be exactly V34 then V35")

    for relative, expected in registration["runner_source_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"V35 panel source drift: {relative}")

    for version in SELECTOR_ORDER:
        row = registration["selectors"][version]
        if set(row) != {"manifest", "manifest_sha256"}:
            raise ValueError(f"invalid {version} selector registration")
        path = ROOT / row["manifest"]
        if sha256_file(path) != row["manifest_sha256"]:
            raise RuntimeError(f"{version} selector manifest drift")
        if json.loads(path.read_text()).get("schema") != SELECTOR_SCHEMAS[version]:
            raise RuntimeError(f"{version} selector schema drift")

    proteins = registration["proteins"]
    if len(proteins) < 2:
        raise ValueError("multi-protein panel requires at least two proteins")
    identities: set[str] = set()
    for row in proteins:
        if set(row) != {"protein_id", "sequence"}:
            raise ValueError("panel inputs contain only protein_id and sequence")
        identity = str(row["protein_id"])
        sequence = str(row["sequence"])
        if identity in identities or not identity.replace("-", "").isalnum():
            raise ValueError("protein identifiers must be unique and path-safe")
        if sequence != sequence.upper() or not sequence or not set(sequence) <= AMINO_ACIDS:
            raise ValueError(f"invalid registered sequence: {identity}")
        identities.add(identity)
    return proteins


def run_panel(registration_path: Path, output_dir: Path) -> dict:
    registration_path, output_dir = map(
        Path.resolve, (registration_path, output_dir))
    if output_dir.exists():
        raise FileExistsError(f"sealed panel output already exists: {output_dir}")
    registration_raw = registration_path.read_bytes()
    registration = json.loads(registration_raw)
    proteins = validate_registration(registration)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix="fold-protein-v35-panel-sealed-", dir=output_dir.parent))
    try:
        (stage / "panel_registration.json").write_bytes(registration_raw)
        inputs_dir = stage / "inputs"
        inputs_dir.mkdir()
        rows = []
        for protein in proteins:
            for version in SELECTOR_ORDER:
                run_id = f"{registration['panel_id']}-{protein['protein_id']}-{version}"
                selector_input = {
                    "run_id": run_id,
                    "sequence": protein["sequence"],
                }
                input_bytes = (
                    json.dumps(selector_input, indent=2, sort_keys=True) + "\n"
                ).encode()
                input_path = inputs_dir / f"{protein['protein_id']}-{version}.json"
                input_path.write_bytes(input_bytes)
                selector = registration["selectors"][version]
                manifest_path = ROOT / selector["manifest"]
                nested_dir = stage / protein["protein_id"] / version
                started = time.perf_counter()
                nested_seal = RUNNERS[version](
                    manifest_path, input_path, nested_dir)
                elapsed = time.perf_counter() - started
                rows.append({
                    "protein_id": protein["protein_id"],
                    "selector_version": version,
                    "run_id": run_id,
                    "sequence_sha256": sha256_bytes(protein["sequence"].encode()),
                    "selector_input_sha256": sha256_bytes(input_bytes),
                    "selector_manifest_sha256": selector["manifest_sha256"],
                    "nested_seal_sha256": sha256_file(nested_dir / "seal.json"),
                    "selected_states_sha256": nested_seal["selected_states_sha256"],
                    "prediction_pdb_sha256": nested_seal["prediction_pdb_sha256"],
                    "elapsed_seconds": elapsed,
                })
        panel_seal = {
            "schema": "fold-protein-v34-v35-paired-panel-seal/v1",
            "status": "completed",
            "result_type": "cumulative development benchmark",
            "official_run": False,
            "execution": registration["execution"],
            "panel_id": registration["panel_id"],
            "panel_registration_sha256": sha256_bytes(registration_raw),
            "runner_source_sha256": registration["runner_source_sha256"],
            "protein_count": len(proteins),
            "prediction_count": len(rows),
            "runs": rows,
        }
        (stage / "panel_seal.json").write_text(
            json.dumps(panel_seal, indent=2, sort_keys=True) + "\n")
        os.replace(stage, output_dir)
        return panel_seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registration", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run_panel(args.registration, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
