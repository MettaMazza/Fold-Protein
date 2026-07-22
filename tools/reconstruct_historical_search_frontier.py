#!/usr/bin/env python3
"""Target-free recovery of the retained V23--V30 search frontiers.

These historical selectors retained a complete 24-path reconciliation before
collapsing it to one emitted structure.  The sealed records preserved only the
emission.  This runner replays the unchanged, source-bound selector, captures
the last complete reconciliation returned by its existing ``_select_unique``
operation, verifies the original emission is reproduced, emits every retained
path, and seals the recovery without accepting a target structure.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v3 import angles_for_state
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb


ROOT = Path(__file__).resolve().parents[1]
VERSIONS = (
    "v23", "v23.1", "v23.2", "v24", "v24.1", "v25",
    "v26", "v26.1", "v27", "v28", "v29", "v30",
)


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


def find_sealed_record(run_id: str) -> tuple[dict, Path, str]:
    matches = []
    for path in (ROOT / "verify/development_runs").glob("*/selected_states.json"):
        record = json.loads(path.read_text())
        if record.get("run_id") == run_id:
            matches.append((record, path))
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one sealed record for {run_id}, found {len(matches)}"
        )
    record, path = matches[0]
    seal_path = path.with_name("seal.json")
    seal = json.loads(seal_path.read_text())
    digest = sha256(path)
    if seal.get("selected_states_sha256") != digest:
        raise RuntimeError(f"lineage selected-state seal drifted: {run_id}")
    return record, path, digest


def domain_trace(record: dict) -> tuple[list, dict]:
    run_id = record.get("domain_run_id") or record.get("parent_run_id")
    if not run_id:
        raise RuntimeError("selector record does not name its domain lineage")
    domain, path, digest = find_sealed_record(run_id)
    if "domain_trace" not in domain:
        raise RuntimeError(f"registered lineage has no domain trace: {run_id}")
    return domain["domain_trace"], {
        "domain_run_id": run_id,
        "domain_selected_states_path": str(path.relative_to(ROOT)),
        "domain_selected_states_sha256": digest,
    }


def selector_arguments(version: str, record: dict) -> tuple[tuple, dict]:
    sequence = record["sequence"].upper()
    if version in ("v23", "v23.1", "v23.2"):
        return (sequence, record["seed_states"]), {}
    domains, lineage = domain_trace(record)
    if version in ("v24", "v24.1", "v25", "v26", "v26.1"):
        return (sequence, record["seed_states"], domains), lineage
    if version == "v27":
        return (
            sequence, record["v25_states"], record["v26_1_states"], domains,
        ), lineage
    branches = [
        record["v25_states"], record["v26_1_states"], record["v27_states"],
    ]
    if version in ("v29", "v30"):
        branches.append(record["v28_states"])
    return (sequence, *branches, domains), lineage


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

    suffix = version.replace(".", "_")
    module = importlib.import_module(f"tools.blind_24_lattice_selector_{suffix}")
    selector = getattr(module, f"select_state_path_{suffix}")
    arguments, lineage = selector_arguments(version, original_states)
    original_select_unique = module._select_unique
    captured = []

    def capture_unique(rows, width):
        retained = original_select_unique(rows, width)
        captured.append(tuple(retained))
        return retained

    module._select_unique = capture_unique
    try:
        result = selector(*arguments)
    finally:
        module._select_unique = original_select_unique

    if not captured:
        raise RuntimeError(f"{version} retained frontier was not captured")
    final_frontier = captured[-1]
    replay_states = list(result["states"])
    if replay_states != original_states["states"]:
        raise RuntimeError(f"{version} replay does not reproduce sealed emission")
    selected_indices = [
        index for index, row in enumerate(final_frontier)
        if list(row[2]) == replay_states
    ]
    if len(selected_indices) != 1:
        raise RuntimeError(
            f"{version} sealed emission occurs {len(selected_indices)} times in frontier"
        )
    selected_index = selected_indices[0]

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(
        prefix=f"fold-protein-{suffix}-frontier-", dir=output_dir.parent
    ))
    try:
        rows, pdb_hashes = [], {}
        for index, row in enumerate(final_frontier):
            states = tuple(row[2])
            name = f"candidate_{index:02d}.pdb"
            emit_states(original_states["sequence"], states, stage / name)
            digest = sha256(stage / name)
            pdb_hashes[name] = digest
            rows.append({
                "candidate_index": index,
                "selected_emission": index == selected_index,
                "hard_exclusion_vector": list(row[0]),
                "objective_vector": list(row[1]),
                "states": list(states),
                "states_sha256": json_sha(list(states)),
                "prediction_pdb": name,
                "prediction_pdb_sha256": digest,
            })
        frontier = {
            "schema": f"fold-protein-{version}-reconstructed-search-frontier/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": original_states["run_id"],
            "original_seal_sha256": sha256(original_seal_path),
            "original_selected_states_sha256": sha256(original_states_path),
            "selected_output_reproduced": True,
            "selected_candidate_index": selected_index,
            "candidate_count": len(rows),
            "lineage": lineage,
            "candidates": rows,
        }
        frontier_path = stage / "frontier.json"
        frontier_path.write_text(json.dumps(frontier, indent=2, sort_keys=True) + "\n")
        seal = {
            "schema": f"fold-protein-{version}-reconstructed-frontier-seal/v1",
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
