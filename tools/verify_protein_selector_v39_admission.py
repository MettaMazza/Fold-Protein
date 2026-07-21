#!/usr/bin/env python3
"""Verify V39 engine/runtime peptide-causal reconciliation admission."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v39 import (
    CAUSAL_AXIS_ORDER,
    CAUSAL_DIRECTION,
    EXPECTED_V38_FIXED_POINTS,
    select_state_path_v39,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v39_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v39.json"
PARENT = ROOT / "verify/development_runs/ubiquitin_v38_coordinate_fixed_point_l76_20260721/selected_states.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v39_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v39-admission/v1":
        raise RuntimeError("unsupported V39 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v39":
        raise RuntimeError("unsupported V39 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V39 admission source drift: {relative}")
    if (CAUSAL_DIRECTION != "n_to_c" or CAUSAL_AXIS_ORDER != (0, 1)
            or EXPECTED_V38_FIXED_POINTS != 4):
        raise RuntimeError("V39 runtime counts differ from engine admission")
    parent = json.loads(PARENT.read_text())
    first = select_state_path_v39(parent["sequence"], parent)
    second = select_state_path_v39(parent["sequence"], parent)
    if first["states"] != second["states"]:
        raise RuntimeError("V39 deterministic replay failed")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v39.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    if project_imports != {"tools.blind_24_lattice_selector_v3"}:
        raise RuntimeError(f"V39 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    if any(term in selector_path.read_text().lower() for term in prohibited):
        raise RuntimeError("V39 selector contains prohibited comparison or fitted input")
    required_roles = {
        "engine_closed_v38_complete_fixed_point_grammar",
        "registered_n_to_c_backbone_construction",
        "engine_closed_phi_then_one_advanced_psi_order",
        "runtime_unique_causal_fixed_point",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V39 minimal composition roles changed")
    return {
        "schema": "fold-protein-selector-v39-admission-verification/v1",
        "status": "verified",
        "parent_fixed_points": EXPECTED_V38_FIXED_POINTS,
        "causal_direction": CAUSAL_DIRECTION,
        "causal_axis_order": list(CAUSAL_AXIS_ORDER),
        "causal_event_ranks": first["causal_event_ranks"],
        "qualifying_fixed_points": 1,
        "deterministic_replay": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v39_admission(), sort_keys=True))
