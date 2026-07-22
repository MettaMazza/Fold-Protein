#!/usr/bin/env python3
"""Run and seal the complete V42 connected backbone-contact frontier."""
from __future__ import annotations

import argparse, hashlib, json, os, shutil, tempfile
from pathlib import Path

from tools.blind_24_lattice_selector_v42 import select_state_frontier_v42
from tools.protein_backbone_geometry_v1 import write_pdb

ROOT = Path(__file__).resolve().parents[1]
PARENT_DIR = ROOT / "verify/development_runs/ubiquitin_v41_component_cube_l76_20260721"

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run_protocol_v42(manifest_path: Path, input_path: Path, output_dir: Path):
    manifest_path, input_path, output_dir = map(Path.resolve, (manifest_path, input_path, output_dir))
    if output_dir.exists(): raise FileExistsError(output_dir)
    manifest_raw, input_raw = manifest_path.read_bytes(), input_path.read_bytes()
    manifest, selector_input = json.loads(manifest_raw), json.loads(input_raw)
    if manifest.get("schema") != "fold-protein-blind-selector/v42": raise ValueError("unsupported V42 manifest")
    if set(selector_input) != {"run_id", "sequence"}: raise ValueError("V42 input must contain exactly run_id and sequence")
    for relative, expected in manifest["source_sha256"].items():
        if sha(ROOT / relative) != expected: raise RuntimeError(f"V42 source drift: {relative}")
    parent_binding = {"seal_sha256": sha(PARENT_DIR / "seal.json"),
                      "selected_states_sha256": sha(PARENT_DIR / "selected_states.json")}
    if manifest.get("parent_v41") != parent_binding: raise RuntimeError("V42 V41 parent drifted")
    parent = json.loads((PARENT_DIR / "selected_states.json").read_text())
    stage = Path(tempfile.mkdtemp(prefix="fold-protein-v42-sealed-", dir=output_dir.parent))
    try:
        (stage / "selector_input.json").write_bytes(input_raw)
        result = select_state_frontier_v42(selector_input["sequence"], parent)
        frontier_rows, pdb_hashes = [], {}
        for row in result["frontier"]:
            pdb_name = f"prediction_mask_{row['mask']}.pdb"
            write_pdb(row["atoms"], stage / pdb_name)
            pdb_hashes[pdb_name] = sha(stage / pdb_name)
            frontier_rows.append({key: value for key, value in row.items() if key != "atoms"})
        record = {
            "schema": "fold-protein-selected-frontier/v42", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "run_id": selector_input["run_id"], "sequence": selector_input["sequence"],
            "blocks": result["blocks"], "block_count": result["block_count"],
            "disagreement_block_count": result["disagreement_block_count"],
            "equal_block_count": result["equal_block_count"],
            "component_cube_candidates": result["component_cube_candidates"],
            "component_cube_trace": result["component_cube_trace"],
            "connected_frontier_count": result["connected_frontier_count"],
            "frontier": frontier_rows, "parallel_workers": result["parallel_workers"],
        }
        frontier_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        (stage / "frontier.json").write_bytes(frontier_bytes)
        seal = {
            "schema": "fold-protein-blind-seal/v42", "status": "completed",
            "result_type": "cumulative development benchmark", "official_run": False,
            "execution": "complete 8192-row whole-chain backbone contact frontier",
            "run_id": selector_input["run_id"],
            "protocol_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "selector_input_sha256": hashlib.sha256(input_raw).hexdigest(),
            "source_sha256": manifest["source_sha256"], "parent_v41": parent_binding,
            "frontier_sha256": hashlib.sha256(frontier_bytes).hexdigest(),
            "prediction_pdb_sha256": pdb_hashes,
            "component_cube_candidates": result["component_cube_candidates"],
            "connected_frontier_count": result["connected_frontier_count"],
            "frontier_masks": [row["mask"] for row in frontier_rows],
        }
        (stage / "seal.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
        os.replace(stage, output_dir)
        return seal
    except Exception:
        shutil.rmtree(stage, ignore_errors=True); raise

if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("manifest",type=Path);p.add_argument("selector_input",type=Path);p.add_argument("output_dir",type=Path)
    a=p.parse_args();print(json.dumps(run_protocol_v42(a.manifest,a.selector_input,a.output_dir),sort_keys=True))
