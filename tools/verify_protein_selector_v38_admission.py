#!/usr/bin/env python3
"""Verify V38 engine/runtime coordinate fixed-point admission."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v38 import (
    AXIS_ORDERS,
    AXIS_VALUE_COUNT,
    DESCENT_ORDERS,
    PAIRED_STATE_COUNT,
    _replace_coordinate,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v38_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v38.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v38_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v38-admission/v1":
        raise RuntimeError("unsupported V38 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v38":
        raise RuntimeError("unsupported V38 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V38 admission source drift: {relative}")
    if (AXIS_VALUE_COUNT != 24 or PAIRED_STATE_COUNT != 576
            or set(AXIS_ORDERS) != {(0, 1), (1, 0)}
            or len(DESCENT_ORDERS) != 4):
        raise RuntimeError("V38 runtime counts differ from engine admission")
    for state in range(PAIRED_STATE_COUNT):
        for axis in (0, 1):
            candidates = {_replace_coordinate(state, axis, value) for value in range(24)}
            if len(candidates) != 24:
                raise RuntimeError("V38 coordinate scan does not exhaust one complete axis")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v38.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    expected_imports = {
        "tools.blind_24_lattice_selector_v3",
        "tools.blind_24_lattice_selector_v37",
    }
    if project_imports != expected_imports:
        raise RuntimeError(f"V38 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    selector_text = selector_path.read_text().lower()
    if any(term in selector_text for term in prohibited):
        raise RuntimeError("V38 selector contains prohibited comparison or fitted input")

    required_roles = {
        "engine_closed_complete_paired_lattice",
        "engine_closed_complete_boundary_axis_order_grammar",
        "complete_one_coordinate_candidate_scans",
        "strict_finite_total_order_termination",
        "admitted_v3_target_free_order",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V38 minimal composition roles changed")
    expected_config = {
        "axis_value_count": 24,
        "coordinate_axis_count": 2,
        "paired_state_count": 576,
        "chain_direction_count": 2,
        "axis_order_count": 2,
        "descent_order_count": 4,
        "parallel_workers": 4,
        "coordinate_candidates_per_scan": 24,
        "convergence": "strict finite total-order fixed point",
        "beam": None,
        "cutoff": None,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest["selector_config"] != expected_config:
        raise RuntimeError("V38 manifest introduces an unregistered component")
    return {
        "schema": "fold-protein-selector-v38-admission-verification/v1",
        "status": "verified",
        "axis_value_count": AXIS_VALUE_COUNT,
        "paired_state_count": PAIRED_STATE_COUNT,
        "axis_orders": [list(order) for order in AXIS_ORDERS],
        "descent_order_count": len(DESCENT_ORDERS),
        "coordinate_scan_exhaustive": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v38_admission(), sort_keys=True))
