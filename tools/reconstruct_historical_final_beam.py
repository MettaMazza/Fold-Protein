#!/usr/bin/env python3
"""Target-free recovery of historical V3--V22 and V34 final beams.

The unchanged selector is replayed under a Python return-frame tracer.  The
tracer copies the selector's already-computed final ``beam``,
``final_candidates`` or ``final_rows`` local before the frame exits.  Every
complete retained path is then emitted and sealed without accepting a target.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]
VERSIONS = tuple(f"v{version}" for version in range(3, 23)) + ("v34",)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, separators=(",", ":")).encode()
    ).hexdigest()


def emit_states(sequence: str, states: tuple[int, ...], path: Path) -> None:
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    write_pdb(build_backbone_coordinates(sequence, phi, psi), path)


def replay_and_capture(version: str, sequence: str):
    module = importlib.import_module(f"tools.blind_24_lattice_selector_{version}")
    selector = getattr(module, f"select_state_path_{version}")
    captured = {}

    def selector_trace(frame, event, arg):
        if event == "return":
            for name in ("final_rows", "final_candidates", "beam"):
                if name in frame.f_locals:
                    captured[name] = list(frame.f_locals[name])
        return selector_trace

    def trace_calls(frame, event, arg):
        if event == "call" and frame.f_code is selector.__code__:
            return selector_trace
        return None

    previous = sys.gettrace()
    sys.settrace(trace_calls)
    try:
        result = selector(sequence)
    finally:
        sys.settrace(previous)
    for name in ("final_rows", "final_candidates", "beam"):
        if name in captured:
            return result, name, captured[name]
    raise RuntimeError(f"{version} final frontier was not visible at return")


def normalise_rows(kind: str, raw_rows: list, terminal_state: int):
    rows = []
    for row in raw_rows:
        if kind == "final_rows":
            hard, objectives, path = row
            relation = {
                "hard_exclusion_vector": list(hard) if isinstance(hard, tuple) else [hard],
                "objective_vector": list(objectives),
            }
        else:
            relation_vector, path = row
            relation = {"selector_relation_vector": list(relation_vector)}
        rows.append((tuple(path) + (terminal_state,), relation))
    return rows


def reconstruct(version: str, manifest_path: Path, input_path: Path,
                original_dir: Path, output_dir: Path) -> dict:
    manifest_path, input_path, original_dir, output_dir = map(
        Path.resolve, (manifest_path, input_path, original_dir, output_dir)
    )
    if output_dir.exists():
        raise FileExistsError(output_dir)
    manifest = json.loads(manifest_path.read_text())
    selector_input = json.loads(input_path.read_text())
    original_seal_path = original_dir / "seal.json"
    original_states_path = original_dir / "selected_states.json"
    original_seal = json.loads(original_seal_path.read_text())
    original_states = json.loads(original_states_path.read_text())
    if manifest.get("schema") != f"fold-protein-blind-selector/{version}":
        raise RuntimeError(f"invalid {version} manifest")
    for relative, expected in manifest["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"{version} source drift: {relative}")
    if original_seal.get("selected_states_sha256") != sha256(original_states_path):
        raise RuntimeError(f"{version} original selected-state seal drifted")
    if original_seal.get("selector_input_sha256") != sha256(input_path):
        raise RuntimeError(f"{version} original selector input seal drifted")
    if selector_input.get("run_id") != original_states.get("run_id"):
        raise RuntimeError(f"{version} input/output run identity drifted")

    sequence = original_states["sequence"].upper()
    result, kind, raw_rows = replay_and_capture(version, sequence)
    if result["states"] != original_states["states"]:
        raise RuntimeError(f"{version} replay does not reproduce sealed emission")
    normalised = normalise_rows(kind, raw_rows, result["states"][-1])
    selected_indices = [
        index for index, (states, _) in enumerate(normalised)
        if list(states) == result["states"]
    ]
    if len(selected_indices) != 1:
        raise RuntimeError(
            f"{version} sealed emission occurs {len(selected_indices)} times in frontier"
        )
    selected_index = selected_indices[0]

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix=f"fold-protein-{version}-beam-", dir=output_dir.parent
    ))
    try:
        rows, pdb_hashes = [], {}
        for index, (states, relation) in enumerate(normalised):
            name = f"candidate_{index:02d}.pdb"
            emit_states(sequence, states, stage / name)
            digest = sha256(stage / name)
            pdb_hashes[name] = digest
            rows.append({
                "candidate_index": index,
                "selected_emission": index == selected_index,
                **relation,
                "states": list(states),
                "states_sha256": json_sha(list(states)),
                "prediction_pdb": name,
                "prediction_pdb_sha256": digest,
            })
        frontier = {
            "schema": f"fold-protein-{version}-reconstructed-final-beam/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": original_states["run_id"],
            "captured_selector_local": kind,
            "original_seal_sha256": sha256(original_seal_path),
            "original_selected_states_sha256": sha256(original_states_path),
            "selected_output_reproduced": True,
            "selected_candidate_index": selected_index,
            "candidate_count": len(rows),
            "candidates": rows,
        }
        frontier_path = stage / "frontier.json"
        frontier_path.write_text(json.dumps(frontier, indent=2, sort_keys=True) + "\n")
        seal = {
            "schema": f"fold-protein-{version}-reconstructed-final-beam-seal/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": original_states["run_id"],
            "protocol_manifest_sha256": sha256(manifest_path),
            "selector_input_sha256": sha256(input_path),
            "original_seal_sha256": frontier["original_seal_sha256"],
            "reconstruction_source_sha256": sha256(Path(__file__).resolve()),
            "selector_source_sha256": manifest["source_sha256"],
            "frontier_sha256": sha256(frontier_path),
            "prediction_pdb_sha256": pdb_hashes,
            "candidate_count": len(rows),
        }
        (stage / "seal.json").write_text(
            json.dumps(seal, indent=2, sort_keys=True) + "\n"
        )
        os.replace(stage, output_dir)
        return seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version", choices=VERSIONS)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("selector_input", type=Path)
    parser.add_argument("original_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(reconstruct(
        args.version, args.manifest, args.selector_input,
        args.original_dir, args.output_dir,
    ), sort_keys=True))


if __name__ == "__main__":
    main()
