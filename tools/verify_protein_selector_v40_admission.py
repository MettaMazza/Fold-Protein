#!/usr/bin/env python3
"""Verify V40 engine/runtime complete lineage paired-state admission."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v40 import (
    CAUSAL_DIRECTION,
    LINEAGE_SEED_COUNT,
    PARALLEL_WORKERS,
    PAIRED_STATE_COUNT,
    _replace_paired_state,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v40_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v40.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v40_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v40-admission/v1":
        raise RuntimeError("unsupported V40 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v40":
        raise RuntimeError("unsupported V40 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V40 admission source drift: {relative}")
    if (LINEAGE_SEED_COUNT != 2 or PAIRED_STATE_COUNT != 576
            or CAUSAL_DIRECTION != "n_to_c" or PARALLEL_WORKERS != 24):
        raise RuntimeError("V40 runtime counts differ from engine admission")
    seed = (14, 201, 0)
    candidates = {
        _replace_paired_state(seed, 1, state)
        for state in range(PAIRED_STATE_COUNT)
    }
    if len(candidates) != PAIRED_STATE_COUNT:
        raise RuntimeError("V40 paired scan does not exhaust all 576 states")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v40.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    expected_imports = {
        "tools.blind_24_lattice_selector_v3",
        "tools.blind_24_lattice_selector_v38",
    }
    if project_imports != expected_imports:
        raise RuntimeError(f"V40 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    if any(term in selector_path.read_text().lower() for term in prohibited):
        raise RuntimeError("V40 selector contains prohibited comparison or fitted input")
    required_roles = {
        "engine_closed_binary_parent_child_lineage",
        "engine_closed_complete_paired_lattice",
        "engine_closed_lineage_paired_cartesian_form",
        "registered_n_to_c_peptide_direction",
        "complete_paired_state_candidate_scans",
        "strict_finite_total_order_termination",
        "admitted_v3_target_free_order",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V40 minimal composition roles changed")
    expected_config = {
        "lineage_seed_count": 2,
        "paired_state_count": 576,
        "updates_per_residue_across_lineage": 1152,
        "causal_direction": "n_to_c",
        "convergence": "strict finite total-order fixed point",
        "parallel_workers": 24,
        "beam": None,
        "cutoff": None,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest["selector_config"] != expected_config:
        raise RuntimeError("V40 manifest introduces an unregistered component")
    return {
        "schema": "fold-protein-selector-v40-admission-verification/v1",
        "status": "verified",
        "lineage_seed_count": LINEAGE_SEED_COUNT,
        "paired_state_count": PAIRED_STATE_COUNT,
        "updates_per_residue_across_lineage": LINEAGE_SEED_COUNT * PAIRED_STATE_COUNT,
        "causal_direction": CAUSAL_DIRECTION,
        "paired_scan_exhaustive": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v40_admission(), sort_keys=True))
