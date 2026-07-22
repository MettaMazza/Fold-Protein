#!/usr/bin/env python3
"""Target-free reconstruction and sealing of historical V31-V33 frontiers.

The historical selectors deterministically generated final retained frontiers
but serialized only their first row. This runner captures the unchanged
selector's complete final `select_balanced_hierarchy` result, verifies that its
first row reproduces the original sealed output, emits every retained structure,
and seals the full frontier without accepting a target path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from tools.blind_24_lattice_selector_v3 import angles_for_state
import tools.blind_24_lattice_selector_v31 as selector_v31
import tools.blind_24_lattice_selector_v32 as selector_v32
import tools.blind_24_lattice_selector_v33 as selector_v33
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates, write_pdb
from tools.run_blind_protocol_v32 import _registered_v32_lineage


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


def load_lineage(version: str, manifest: dict, selector_input: dict):
    sequence = selector_input["sequence"].upper()
    lineage_manifest = manifest
    if version == "v33":
        lineage_manifest = json.loads(
            (ROOT / "verify/blind_selector_v32.json").read_text()
        )
    return _registered_v32_lineage(
        lineage_manifest, selector_input["parent_run_id"], sequence
    )


def reconstruct(version: str, manifest_path: Path, input_path: Path,
                original_dir: Path, output_dir: Path) -> dict:
    manifest_path = manifest_path.resolve()
    input_path = input_path.resolve()
    original_dir = original_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)

    manifest = json.loads(manifest_path.read_text())
    selector_input = json.loads(input_path.read_text())
    if manifest.get("schema") != f"fold-protein-blind-selector/{version}":
        raise RuntimeError(f"invalid {version} manifest")
    if set(selector_input) != {"run_id", "sequence", "parent_run_id"}:
        raise RuntimeError(f"invalid {version} selector input")
    for relative, expected in manifest["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"{version} source drift: {relative}")

    original_seal = json.loads((original_dir / "seal.json").read_text())
    original_states = json.loads((original_dir / "selected_states.json").read_text())
    if (original_seal.get("selected_states_sha256")
            != sha256(original_dir / "selected_states.json")):
        raise RuntimeError(f"{version} original selected-state seal drifted")
    if original_seal.get("selector_input_sha256") != sha256(input_path):
        raise RuntimeError(f"{version} original input seal drifted")

    v25, v261, v27, v28, v29, v30, domain, _, _ = load_lineage(
        version, manifest, selector_input
    )
    module = {"v31": selector_v31, "v32": selector_v32, "v33": selector_v33}[version]
    selector = getattr(module, f"select_state_path_{version}")
    original_balance = module.select_balanced_hierarchy
    captured = []

    def capture_balance(rows, capacity):
        retained = original_balance(rows, capacity)
        captured.append(retained)
        return retained

    module.select_balanced_hierarchy = capture_balance
    try:
        result = selector(
            selector_input["sequence"].upper(),
            v25["states"], v261["states"], v27["states"], v28["states"],
            v29["states"], v30["states"], domain["domain_trace"],
        )
    finally:
        module.select_balanced_hierarchy = original_balance

    if not captured:
        raise RuntimeError(f"{version} final frontier was not captured")
    final_frontier = captured[-1]
    if list(final_frontier[0][2]) != result["states"]:
        raise RuntimeError(f"{version} captured frontier does not lead the replay")
    if result["states"] != original_states["states"]:
        raise RuntimeError(f"{version} replay does not reproduce original selection")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f"fold-protein-{version}-frontier-",
                                  dir=output_dir.parent))
    try:
        frontier_rows = []
        pdb_hashes = {}
        for index, row in enumerate(final_frontier):
            states = tuple(row[2])
            name = f"candidate_{index:02d}.pdb"
            emit_states(selector_input["sequence"].upper(), states, stage / name)
            pdb_hashes[name] = sha256(stage / name)
            frontier_rows.append({
                "candidate_index": index,
                "selected_emission": index == 0,
                "hard_exclusion_vector": list(row[0]),
                "objective_vector": list(row[1]),
                "states": list(states),
                "states_sha256": json_sha(list(states)),
                "prediction_pdb": name,
                "prediction_pdb_sha256": pdb_hashes[name],
            })
        frontier = {
            "schema": f"fold-protein-{version}-reconstructed-complete-frontier/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "original_seal_sha256": sha256(original_dir / "seal.json"),
            "original_selected_states_sha256": sha256(
                original_dir / "selected_states.json"
            ),
            "selected_output_byte_reproduced": True,
            "candidate_count": len(frontier_rows),
            "candidates": frontier_rows,
        }
        frontier_path = stage / "frontier.json"
        frontier_path.write_text(json.dumps(frontier, indent=2, sort_keys=True) + "\n")
        seal = {
            "schema": f"fold-protein-{version}-reconstructed-frontier-seal/v1",
            "status": "completed",
            "result_type": "target-free historical frontier reconstruction",
            "official_run": False,
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": sha256(manifest_path),
            "selector_input_sha256": sha256(input_path),
            "original_seal_sha256": frontier["original_seal_sha256"],
            "reconstruction_source_sha256": sha256(Path(__file__).resolve()),
            "selector_source_sha256": manifest["source_sha256"],
            "frontier_sha256": sha256(frontier_path),
            "prediction_pdb_sha256": pdb_hashes,
            "candidate_count": len(frontier_rows),
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
    parser.add_argument("version", choices=("v31", "v32", "v33"))
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
