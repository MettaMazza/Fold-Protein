#!/usr/bin/env python3
"""Verify complete V36 two-boundary reconciliation admission."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v36 import (
    BOUNDARY_CONTEXTS,
    CHAIN_BOUNDARIES,
    COMPLETE_CHAIN_CANDIDATES,
    select_state_path_v36,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v36_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v36.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v36_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v36-admission/v1":
        raise RuntimeError("unsupported V36 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v36":
        raise RuntimeError("unsupported V36 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V36 admission source drift: {relative}")
    if (CHAIN_BOUNDARIES != 2 or BOUNDARY_CONTEXTS != 8
            or COMPLETE_CHAIN_CANDIDATES != 16):
        raise RuntimeError("V36 runtime counts differ from engine admission")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v36.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    expected_imports = {
        "tools.blind_24_lattice_selector_v3",
        "tools.blind_24_lattice_selector_v34",
        "tools.blind_24_lattice_selector_v35",
    }
    if project_imports != expected_imports:
        raise RuntimeError(f"V36 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    selector_text = selector_path.read_text().lower()
    if any(term in selector_text for term in prohibited):
        raise RuntimeError("V36 selector contains prohibited comparison or fitted input")

    sequence = "MQIFVKTL"
    first, second = select_state_path_v36(sequence), select_state_path_v36(sequence)
    if (first["states"] != second["states"]
            or first["reconciliation_trace"] != second["reconciliation_trace"]):
        raise RuntimeError("V36 deterministic replay failed")
    if (len(first["reconciliation_trace"]) != 16
            or set(first["candidates_per_boundary"].values()) != {8}):
        raise RuntimeError("V36 complete candidate grammar is not preserved")

    required_roles = {
        "engine_closed_candidate_domain",
        "engine_closed_boundary_graph",
        "engine_closed_two_boundary_candidate_form",
        "admitted_v3_target_free_order",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V36 minimal composition roles changed")
    expected_config = {
        "candidate_domain": {"alpha": 201, "beta": 117},
        "candidate_domain_count": 2,
        "chain_boundaries": 2,
        "boundary_contexts": 8,
        "candidates_per_boundary": 8,
        "complete_chain_candidates": 16,
        "representatives_per_context_per_boundary": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest["selector_config"] != expected_config:
        raise RuntimeError("V36 manifest introduces an unregistered component")
    return {
        "schema": "fold-protein-selector-v36-admission-verification/v1",
        "status": "verified",
        "chain_boundaries": CHAIN_BOUNDARIES,
        "boundary_contexts": BOUNDARY_CONTEXTS,
        "complete_chain_candidates": COMPLETE_CHAIN_CANDIDATES,
        "deterministic_replay": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v36_admission(), sort_keys=True))
