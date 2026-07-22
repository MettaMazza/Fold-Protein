#!/usr/bin/env python3
"""Reconstruct and seal every complete V35 boundary-context path target-free."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    _candidate_key,
    angles_for_state,
)
from tools.blind_24_lattice_selector_v34 import (
    BINARY_COUNT,
    _whole_power,
    closed_angle_domain,
)
from tools.blind_24_lattice_selector_v35 import (
    BOUNDARY_CONTEXTS,
    BOUNDARY_RESIDUES,
    _context,
    select_state_path_v35,
)
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]


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


def reconstruct_final_frontier(sequence: str):
    candidate_states = tuple(sorted(closed_angle_domain().values()))
    if len(candidate_states) != BINARY_COUNT or BOUNDARY_CONTEXTS != 8:
        raise RuntimeError("V35 boundary census changed")
    frontier = [((0, 1.0, 0.0), tuple())]
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in frontier:
            for state in candidate_states:
                candidate = path + (state,)
                expanded.append((_candidate_key(sequence, list(candidate)), candidate))
        if index + 1 < BOUNDARY_RESIDUES:
            frontier = sorted(expanded, key=lambda item: (item[0], item[1]))
        else:
            grouped = {}
            for item in expanded:
                grouped.setdefault(_context(item[1]), []).append(item)
            if len(grouped) != BOUNDARY_CONTEXTS:
                raise RuntimeError("V35 final boundary census changed")
            frontier = []
            for context in sorted(grouped):
                arrivals = sorted(grouped[context], key=lambda item: (item[0], item[1]))
                expected = 1 if index + 1 == BOUNDARY_RESIDUES else BINARY_COUNT
                if len(arrivals) != expected:
                    raise RuntimeError("V35 inbound transition census changed")
                frontier.append(arrivals[0])
            frontier.sort(key=lambda item: (item[0], item[1]))
    if len(frontier) != BOUNDARY_CONTEXTS:
        raise RuntimeError("V35 complete frontier did not contain eight paths")
    return frontier


def reconstruct(manifest_path: Path, input_path: Path, original_dir: Path,
                output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    original_dir = original_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)

    manifest = json.loads(manifest_path.read_text())
    selector_input = json.loads(input_path.read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v35":
        raise RuntimeError("invalid V35 manifest")
    if set(selector_input) != {"run_id", "sequence"}:
        raise RuntimeError("invalid V35 selector input")
    for relative, expected in manifest["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V35 source drift: {relative}")

    original_seal = json.loads((original_dir / "seal.json").read_text())
    original_states = json.loads((original_dir / "selected_states.json").read_text())
    if original_seal.get("selected_states_sha256") != sha256(
        original_dir / "selected_states.json"
    ):
        raise RuntimeError("V35 selected-state seal drifted")
    if original_seal.get("selector_input_sha256") != sha256(input_path):
        raise RuntimeError("V35 input seal drifted")

    sequence = selector_input["sequence"].upper()
    replay = select_state_path_v35(sequence)
    if replay["states"] != original_states["states"]:
        raise RuntimeError("V35 selector replay does not reproduce the sealed row")
    frontier = reconstruct_final_frontier(sequence)
    full_states = [tuple(path) + (CANONICAL_STATE,) for _, path in frontier]
    if list(full_states[0]) != original_states["states"]:
        raise RuntimeError("V35 reconstructed frontier does not lead with sealed row")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v35-frontier-",
                                  dir=output_dir.parent))
    try:
        rows = []
        pdb_hashes = {}
        for index, ((rank_key, _), states) in enumerate(zip(frontier, full_states)):
            name = f"candidate_{index:02d}.pdb"
            emit_states(sequence, states, stage / name)
            pdb_hashes[name] = sha256(stage / name)
            rows.append({
                "candidate_index": index,
                "selected_emission": index == 0,
                "boundary_context": list(states[-4:-1]),
                "rank_key": list(rank_key),
                "states": list(states),
                "states_sha256": json_sha(list(states)),
                "prediction_pdb": name,
                "prediction_pdb_sha256": pdb_hashes[name],
            })
        if sha256(stage / "candidate_00.pdb") != sha256(original_dir / "prediction.pdb"):
            raise RuntimeError("V35 reconstructed emission is not byte-identical")
        evidence = {
            "schema": "fold-protein-v35-reconstructed-complete-frontier/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "original_seal_sha256": sha256(original_dir / "seal.json"),
            "original_selected_states_sha256": sha256(
                original_dir / "selected_states.json"
            ),
            "selected_output_byte_reproduced": True,
            "candidate_count": len(rows),
            "candidates": rows,
        }
        frontier_path = stage / "frontier.json"
        frontier_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        seal = {
            "schema": "fold-protein-v35-reconstructed-frontier-seal/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256(manifest_path),
            "selector_input_sha256": sha256(input_path),
            "original_seal_sha256": evidence["original_seal_sha256"],
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
    parser.add_argument("manifest", type=Path)
    parser.add_argument("selector_input", type=Path)
    parser.add_argument("original_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(reconstruct(
        args.manifest, args.selector_input, args.original_dir, args.output_dir
    ), sort_keys=True))


if __name__ == "__main__":
    main()
