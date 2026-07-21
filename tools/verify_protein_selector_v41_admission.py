#!/usr/bin/env python3
"""Verify V41 connected-component cube admission."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v41 import (
    EXPECTED_COMPONENTS, EXPECTED_CUBE_CANDIDATES, EXPECTED_DISAGREEMENTS,
    component_cube_candidate, maximal_disagreement_components,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v41_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v41.json"
PARENT = ROOT / "verify/development_runs/ubiquitin_v40_lineage_paired_fixed_point_l76_20260721/selected_states.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v41_admission() -> dict:
    receipt, manifest = json.loads(RECEIPT.read_text()), json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v41-admission/v1" or manifest.get("schema") != "fold-protein-blind-selector/v41":
        raise RuntimeError("unsupported V41 admission")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected: raise RuntimeError(f"V41 source drift: {relative}")
    parent = json.loads(PARENT.read_text())
    by_seed = {row["seed"]: tuple(row["path"]) for row in parent["fixed_point_trace"]}
    left, right = by_seed["v38_parent"], by_seed["v39_causal_child"]
    components = maximal_disagreement_components(left, right)
    disagreements, candidates = sum(map(len, components)), 1 << len(components)
    if (disagreements, len(components), candidates) != (EXPECTED_DISAGREEMENTS, EXPECTED_COMPONENTS, EXPECTED_CUBE_CANDIDATES):
        raise RuntimeError("V41 runtime component census differs from engine admission")
    if component_cube_candidate(left, right, components, 0) != left or component_cube_candidate(left, right, components, candidates - 1) != right:
        raise RuntimeError("V41 complete cube does not contain both parent rows")
    tree = ast.parse((ROOT / "tools/blind_24_lattice_selector_v41.py").read_text())
    imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("tools.")}
    if imports != {"tools.blind_24_lattice_selector_v3", "tools.blind_24_lattice_selector_v38", "tools.blind_24_lattice_selector_v40"}:
        raise RuntimeError(f"V41 imports unadmitted runtime routes: {sorted(imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    if any(term in (ROOT / "tools/blind_24_lattice_selector_v41.py").read_text().lower() for term in prohibited):
        raise RuntimeError("V41 selector contains prohibited comparison input")
    return {
        "schema": "fold-protein-selector-v41-admission-verification/v1", "status": "verified",
        "disagreement_count": disagreements, "component_count": len(components),
        "component_cube_candidates": candidates, "parents_in_cube": True,
    }


if __name__ == "__main__": print(json.dumps(verify_selector_v41_admission(), sort_keys=True))
