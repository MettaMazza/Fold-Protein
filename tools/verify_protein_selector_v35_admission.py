#!/usr/bin/env python3
"""Verify complete V35 boundary propagation before target comparison."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v35 import (
    BOUNDARY_CONTEXTS,
    QUARTET_TRANSITIONS,
    select_state_path_v35,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v35_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v35.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v35_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v35-admission/v1":
        raise RuntimeError("unsupported V35 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v35":
        raise RuntimeError("unsupported V35 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V35 admission source drift: {relative}")
    if BOUNDARY_CONTEXTS != 8 or QUARTET_TRANSITIONS != 16:
        raise RuntimeError("V35 runtime graph differs from the engine counts")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v35.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    expected_imports = {
        "tools.blind_24_lattice_selector_v3",
        "tools.blind_24_lattice_selector_v34",
    }
    if project_imports != expected_imports:
        raise RuntimeError(f"V35 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    selector_text = selector_path.read_text().lower()
    if any(term in selector_text for term in prohibited):
        raise RuntimeError("V35 selector contains prohibited comparison or fitted input")

    sequence = "MQIFVKTL"
    first, second = select_state_path_v35(sequence), select_state_path_v35(sequence)
    if first["states"] != second["states"] or first["boundary_trace"] != second["boundary_trace"]:
        raise RuntimeError("V35 deterministic replay failed")
    for row in first["boundary_trace"][3:]:
        if (row["candidate_domain"] != [117, 201]
                or row["expanded_transitions"] != 16
                or row["retained_contexts"] != 8
                or row["inbound_per_context"] != [2]):
            raise RuntimeError("V35 complete boundary graph is not preserved")

    required_roles = {
        "engine_closed_candidate_domain",
        "engine_closed_boundary_graph",
        "admitted_v3_target_free_order",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V35 minimal composition roles changed")
    expected_config = {
        "candidate_domain": {"alpha": 201, "beta": 117},
        "candidate_domain_count": 2,
        "boundary_residues": 3,
        "boundary_contexts": 8,
        "quartet_residues": 4,
        "quartet_transitions": 16,
        "representatives_per_context": 1,
        "lookahead_residues": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest["selector_config"] != expected_config:
        raise RuntimeError("V35 manifest introduces an unregistered component")
    return {
        "schema": "fold-protein-selector-v35-admission-verification/v1",
        "status": "verified",
        "boundary_contexts": BOUNDARY_CONTEXTS,
        "quartet_transitions": QUARTET_TRANSITIONS,
        "deterministic_replay": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v35_admission(), sort_keys=True))
