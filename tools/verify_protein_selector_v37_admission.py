#!/usr/bin/env python3
"""Verify V37 engine/runtime whole-chain generator-partition admission."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools.blind_24_lattice_selector_v37 import select_state_path_v37


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_selector_v37_admission_v1.json"
MANIFEST = ROOT / "verify/blind_selector_v37.json"
UBIQUITIN = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v37_admission() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if receipt.get("schema") != "fold-protein-selector-v37-admission/v1":
        raise RuntimeError("unsupported V37 admission receipt")
    if manifest.get("schema") != "fold-protein-blind-selector/v37":
        raise RuntimeError("unsupported V37 selector manifest")
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V37 admission source drift: {relative}")

    selector_path = ROOT / "tools/blind_24_lattice_selector_v37.py"
    tree = ast.parse(selector_path.read_text())
    project_imports = {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        and (node.module.startswith("tools.") or node.module.startswith("verify."))
    }
    expected_imports = {
        "tools.blind_24_lattice_selector_v3",
        "tools.blind_24_lattice_selector_v34",
        "tools.blind_24_lattice_selector_v36",
    }
    if project_imports != expected_imports:
        raise RuntimeError(f"V37 imports an unadmitted runtime route: {sorted(project_imports)}")
    prohibited = ("target_pdb", "parse_pdb", "compute_tm", "reward", "trained_parameter")
    selector_text = selector_path.read_text().lower()
    if any(term in selector_text for term in prohibited):
        raise RuntimeError("V37 selector contains prohibited comparison or fitted input")

    first, second = select_state_path_v37(UBIQUITIN), select_state_path_v37(UBIQUITIN)
    if first["states"] != second["states"] or first["census_trace"] != second["census_trace"]:
        raise RuntimeError("V37 deterministic replay failed")
    if (first["complete_chain_candidates"] != 16
            or first["partition_span"] != 5
            or first["partition_unit_count"] != 15
            or first["expected_unordered_mode_census"] != [30, 45]
            or first["qualifying_candidates"] != 1
            or sum(row["qualifies"] for row in first["census_trace"]) != 1):
        raise RuntimeError("V37 runtime relation differs from engine admission")

    required_roles = {
        "engine_closed_candidate_domain",
        "engine_closed_complete_two_boundary_grammar",
        "engine_closed_unordered_generator_partition",
        "runtime_unique_partition_candidate",
        "target_incapable_geometry",
        "seal_before_comparison",
    }
    if set(receipt["minimal_composition_roles"]) != required_roles:
        raise RuntimeError("V37 minimal composition roles changed")
    expected_config = {
        "candidate_domain": {"alpha": 201, "beta": 117},
        "candidate_domain_count": 2,
        "complete_chain_candidates": 16,
        "partition_generators": [2, 3],
        "partition_span": 5,
        "mode_assignment": None,
        "required_qualifying_candidates": 1,
        "target": None,
        "template": None,
        "reward": None,
        "weight": None,
        "trained_parameter": None,
    }
    if manifest["selector_config"] != expected_config:
        raise RuntimeError("V37 manifest introduces an unregistered component")
    return {
        "schema": "fold-protein-selector-v37-admission-verification/v1",
        "status": "verified",
        "registered_sequence_length": len(UBIQUITIN),
        "active_state_count": len(UBIQUITIN) - 1,
        "partition_span": first["partition_span"],
        "partition_unit_count": first["partition_unit_count"],
        "expected_unordered_mode_census": first["expected_unordered_mode_census"],
        "complete_chain_candidates": first["complete_chain_candidates"],
        "qualifying_candidates": first["qualifying_candidates"],
        "deterministic_replay": True,
        "minimal_composition_roles": sorted(required_roles),
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v37_admission(), sort_keys=True))
