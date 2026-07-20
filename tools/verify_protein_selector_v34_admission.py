#!/usr/bin/env python3
"""Verify the V34 composition before any target comparison is permitted."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v34 import (
    closed_angle_domain, select_state_path_v34)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v34_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v34.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v34_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v34-admission/v1":
        raise RuntimeError("unsupported V34 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v34":
        raise RuntimeError("unsupported V34 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V34 admission source drift: {relative}")

    engine = json.loads((ROOT / "verify/protein_engine_closure_v1.json").read_text())
    counts = engine["closed_relations"]["canonical_angle_forms"]["complete_candidate_counts"]
    if set(counts.values()) != {1}:
        raise RuntimeError("V34 dependency has lost canonical-angle uniqueness")
    if closed_angle_domain() != {"alpha": 201, "beta": 117}:
        raise RuntimeError("V34 runtime domain differs from the engine-closed forms")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v34.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    if project_imports != {"tools.blind_24_lattice_selector_v3"}:
        raise RuntimeError(f"V34 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    selector_text = selector_path.read_text().lower()
    if any(term in selector_text for term in prohibited):
        raise RuntimeError("V34 selector contains prohibited comparison or fitted input")

    sequence = "MQIFVKTL"
    first = select_state_path_v34(sequence)
    second = select_state_path_v34(sequence)
    if first["states"] != second["states"] or first["score_trace"] != second["score_trace"]:
        raise RuntimeError("V34 deterministic uniqueness replay failed")
    prior_retained = 1
    for row in first["score_trace"]:
        if row["candidate_domain"] != [117, 201]:
            raise RuntimeError("V34 did not enumerate the complete closed domain")
        if row["expanded"] != prior_retained * 2:
            raise RuntimeError("V34 assembled candidate grammar is incomplete")
        prior_retained = row["retained"]

    required_roles = {
        "engine_closed_candidate_domain",
        "admitted_v3_target_free_order",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V34 minimal composition roles changed")
    if manifest["selector_config"] != {
        "beam_width": 24,
        "candidate_domain": {"alpha": 201, "beta": 117},
        "candidate_domain_count": 2,
        "lookahead_residues": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }:
        raise RuntimeError("V34 manifest introduces an unregistered component")
    return {
        "schema": "fold-protein-selector-v34-admission-verification/v1",
        "status": "verified",
        "candidate_domain": closed_angle_domain(),
        "candidate_domain_count": 2,
        "deterministic_replay": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v34_admission(), sort_keys=True))
