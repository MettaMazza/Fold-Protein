#!/usr/bin/env python3
"""Exhaustively verify and register protein material architecture V1."""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
from typing import Optional

from tools.protein_material_architecture_v1 import materialise_protein_relation


ROOT = Path(__file__).resolve().parents[1]
RELATION = ROOT / "verify/protein_material_relation_v1.json"
COMPARISON = ROOT / "verify/protected_path_recovered_frontier_comparison_v1.json"
ARCHITECTURE = ROOT / "tools/protein_material_architecture_v1.py"
ADMISSION = ROOT / "constants/protein_material_architecture_v1_admission.ep"
ENGINE_TEST = ROOT / "tests/test_protein_material_architecture_v1_admission.ep"
OUTPUT = ROOT / "verify/protein_material_architecture_v1_admission.json"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(raw).hexdigest()


def verify_import_boundary():
    tree = ast.parse(ARCHITECTURE.read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    allowed = {
        "__future__", "hashlib", "json", "numpy",
        "tools.blind_24_lattice_selector_v3",
    }
    unexpected = sorted(set(imports) - allowed)
    if unexpected:
        raise RuntimeError(f"material runtime import boundary expanded: {unexpected}")
    return sorted(set(imports))


def verify_material_architecture_v1(output_path: Optional[Path] = OUTPUT):
    relation = json.loads(RELATION.read_text())
    if relation.get("schema") != "fold-protein-material-relation/v1":
        raise RuntimeError("material relation schema drifted")
    comparison = json.loads(COMPARISON.read_text())
    if relation["source_binding"]["comparison_sha256"] != file_sha256(COMPARISON):
        raise RuntimeError("material relation comparison binding drifted")
    if relation["comparison_census"] != {
        "comparison_sha256": file_sha256(COMPARISON),
        "full_length_compared_candidates": 10159,
        "full_length_exact_state_relation_matches": 0,
        "full_length_exact_contact_relation_matches": 0,
        "full_length_exact_long_range_orientation_matches": 0,
        "recovered_candidates_all_lengths": 10336,
        "active_extension_candidates": 1097,
    }:
        raise RuntimeError("complete frontier distinction census drifted")
    if comparison["census"]["total_compared_candidates"] != 11433:
        raise RuntimeError("protected comparison candidate census drifted")

    imports = verify_import_boundary()
    result = materialise_protein_relation(relation["sequence"], relation)
    expected_raw = relation["residue_count"] * relation["lattice_state_count"]
    expected_matches = (
        relation["residue_count"] - 2 + 2 * relation["lattice_axis_count"]
    )
    if result["complete_raw_state_candidates"] != expected_raw:
        raise RuntimeError("complete 576-state-per-residue census drifted")
    if result["complete_raw_signature_matches"] != expected_matches:
        raise RuntimeError("material signature match census drifted")
    if result["unique_material_states"] != relation["residue_count"]:
        raise RuntimeError("material relation did not yield one state per residue")
    if canonical_sha256(result["states"]) != relation["source_binding"][
            "protected_states_sha256"]:
        raise RuntimeError("material reconstruction differs from protected state identity")
    if (result["window_geometry_checks"] != 74
            or result["quartet_geometry_checks"] != 73
            or result["contact_relation_checks"] != 40
            or result["long_range_orientation_checks"] != 2628):
        raise RuntimeError("complete generated-geometry closure drifted")
    if any(result[key] != 0 for key in (
        "candidate_orderings", "weights", "fitted_parameters",
        "runtime_target_accesses",
    )):
        raise RuntimeError("prohibited runtime mechanism became active")

    receipt = {
        "schema": "fold-protein-material-architecture-admission/v1",
        "status": "admitted",
        "result_type": "target-assisted prevalidation receipt",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "complete_construction": {
            "residue_count": relation["residue_count"],
            "lattice_state_count_per_residue": relation["lattice_state_count"],
            "complete_raw_state_candidates": result[
                "complete_raw_state_candidates"
            ],
            "complete_raw_signature_matches": result[
                "complete_raw_signature_matches"
            ],
            "interior_unique_signature_matches": relation["residue_count"] - 2,
            "n_boundary_phi_gauge_equivalents": relation["lattice_axis_count"],
            "c_boundary_psi_gauge_equivalents": relation["lattice_axis_count"],
            "unique_material_states_after_gauge": result[
                "unique_material_states"
            ],
            "sequence_window_count": result["window_geometry_checks"],
            "quartet_count": result["quartet_geometry_checks"],
            "contact_relation_count": result["contact_relation_checks"],
            "long_range_orientation_count": result[
                "long_range_orientation_checks"
            ],
            "candidate_orderings": result["candidate_orderings"],
            "weights": result["weights"],
            "fitted_parameters": result["fitted_parameters"],
            "runtime_target_accesses": result["runtime_target_accesses"],
            "states_sha256": canonical_sha256(result["states"]),
        },
        "frontier_distinction": relation["comparison_census"],
        "runtime_imports": imports,
        "source_sha256": {
            str(RELATION.relative_to(ROOT)): file_sha256(RELATION),
            str(COMPARISON.relative_to(ROOT)): file_sha256(COMPARISON),
            str(ARCHITECTURE.relative_to(ROOT)): file_sha256(ARCHITECTURE),
            str(ADMISSION.relative_to(ROOT)): file_sha256(ADMISSION),
            str(ENGINE_TEST.relative_to(ROOT)): file_sha256(ENGINE_TEST),
            str(Path(__file__).resolve().relative_to(ROOT)): file_sha256(
                Path(__file__).resolve()
            ),
        },
        "author_audit": {
            "author": "OpenAI Codex",
            "model": "GPT-5",
            "reasoning_level": "high",
        },
    }
    if output_path is not None:
        output_path = output_path.resolve()
        output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = verify_material_architecture_v1(args.output)
    print(json.dumps(result["complete_construction"], sort_keys=True))


if __name__ == "__main__":
    main()
