#!/usr/bin/env python3
"""Run and atomically seal a registered selector-v2 real-sequence length ladder."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time

try:
    from tools.run_blind_protocol_v2 import run_protocol_v2
except ImportError:
    from run_blind_protocol_v2 import run_protocol_v2


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(record: dict) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


def validate_registration(path: Path) -> tuple[dict, bytes]:
    raw = path.resolve().read_bytes()
    registration = json.loads(raw)
    if registration.get("schema") != "fold-protein-selector-v2-length-ladder/v1":
        raise ValueError("unsupported selector-v2 length ladder")
    sequence = registration["sequence"].upper()
    if sha256_bytes(sequence.encode()) != registration["sequence_sha256"]:
        raise RuntimeError("registered sequence hash mismatch")
    lengths = registration["lengths"]
    if lengths != sorted(set(lengths)) or not lengths or lengths[-1] != len(sequence):
        raise ValueError("lengths must be unique ascending prefixes ending at full length")
    if any(length < 2 or length > len(sequence) for length in lengths):
        raise ValueError("registered prefix length outside sequence")
    manifest = ROOT / registration["selector_manifest"]
    if sha256_file(manifest) != registration["selector_manifest_sha256"]:
        raise RuntimeError("selector-v2 manifest drift")
    for relative, expected in registration["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"length-ladder source drift: {relative}")
    return registration, raw


def run_ladder(registration_path: Path, output_dir: Path) -> dict:
    registration, registration_raw = validate_registration(registration_path)
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"sealed length ladder already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v2-ladder-",
                                  dir=output_dir.parent))
    receipts = []
    failures = 0
    try:
        (stage / "ladder_registration.json").write_bytes(registration_raw)
        sequence = registration["sequence"].upper()
        manifest = ROOT / registration["selector_manifest"]
        for length in registration["lengths"]:
            run_id = f"{registration['run_id']}-l{length}"
            if not RUN_ID.fullmatch(run_id):
                raise ValueError(f"invalid derived run_id: {run_id}")
            input_record = {"run_id": run_id, "sequence": sequence[:length]}
            input_path = stage / f"{run_id}-input.json"
            input_path.write_bytes(json_bytes(input_record))
            run_dir = stage / run_id
            started = time.monotonic()
            try:
                nested = run_protocol_v2(manifest, input_path, run_dir)
                elapsed = time.monotonic() - started
                receipt = {
                    "length": length,
                    "run_id": run_id,
                    "status": "completed",
                    "candidate_count": 24 + 24 * 576 * (length - 2),
                    "elapsed_seconds": elapsed,
                    "nested_seal_sha256": sha256_file(run_dir / "seal.json"),
                    "selected_states_sha256": nested["selected_states_sha256"],
                    "prediction_pdb_sha256": nested["prediction_pdb_sha256"],
                }
            except Exception as error:
                failures += 1
                elapsed = time.monotonic() - started
                receipt = {
                    "length": length,
                    "run_id": run_id,
                    "status": "failed",
                    "candidate_count": 24 + 24 * 576 * (length - 2),
                    "elapsed_seconds": elapsed,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            receipt_path = stage / f"{run_id}-execution.json"
            receipt_path.write_bytes(json_bytes(receipt))
            receipts.append({**receipt, "execution_sha256": sha256_file(receipt_path)})
        seal = {
            "schema": "fold-protein-selector-v2-length-ladder-seal/v1",
            "status": "completed" if failures == 0 else "completed_with_failures",
            "execution": "ubiquitin sequence selector-v2 length ladder",
            "registration_sha256": sha256_bytes(registration_raw),
            "runs": receipts,
        }
        (stage / "ladder_seal.json").write_bytes(json_bytes(seal))
        os.replace(stage, output_dir)
        return seal
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registration", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run_ladder(args.registration, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
