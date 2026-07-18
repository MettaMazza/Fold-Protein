#!/usr/bin/env python3
"""Execute and seal a registered selector-v2 sequence-only diagnostic panel."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

try:
    from tools.run_blind_protocol_v2 import run_protocol_v2
except ImportError:
    from run_blind_protocol_v2 import run_protocol_v2


ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(record: dict) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


def run_panel(panel_path: Path, output_dir: Path) -> dict:
    panel_path = panel_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"sealed panel output already exists: {output_dir}")
    panel_raw = panel_path.read_bytes()
    panel = json.loads(panel_raw)
    if panel.get("schema") != "fold-protein-selector-v2-panel/v1":
        raise ValueError("unsupported selector-v2 panel")
    selector_manifest = ROOT / panel["selector_manifest"]
    if sha256_file(selector_manifest) != panel["selector_manifest_sha256"]:
        raise RuntimeError("selector-v2 manifest drift")
    for relative, expected in panel["runner_source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"panel runner source drift: {relative}")
    run_ids = [row["run_id"] for row in panel["sequences"]]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("panel run_id values must be unique")
    for row in panel["sequences"]:
        if set(row) != {"run_id", "sequence", "diagnostic_role"}:
            raise ValueError("panel rows may contain only run_id, sequence, diagnostic_role")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v2-panel-", dir=output_dir.parent))
    receipts = []
    try:
        (stage / "panel_registration.json").write_bytes(panel_raw)
        for row in panel["sequences"]:
            input_path = stage / f"{row['run_id']}-input.json"
            input_path.write_bytes(json_bytes(
                {"run_id": row["run_id"], "sequence": row["sequence"]}))
            run_dir = stage / row["run_id"]
            seal = run_protocol_v2(selector_manifest, input_path, run_dir)
            receipts.append({
                "run_id": row["run_id"],
                "diagnostic_role": row["diagnostic_role"],
                "seal_sha256": sha256_file(run_dir / "seal.json"),
                "selected_states_sha256": seal["selected_states_sha256"],
                "prediction_pdb_sha256": seal["prediction_pdb_sha256"],
            })
        panel_seal = {
            "schema": "fold-protein-selector-v2-panel-seal/v1",
            "status": "completed",
            "execution": "five-sequence selector-v2 panel",
            "panel_registration_sha256": sha256_bytes(panel_raw),
            "runs": receipts,
        }
        (stage / "panel_seal.json").write_bytes(json_bytes(panel_seal))
        os.replace(stage, output_dir)
        return panel_seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(run_panel(args.panel, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
