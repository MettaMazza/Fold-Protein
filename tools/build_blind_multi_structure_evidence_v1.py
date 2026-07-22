#!/usr/bin/env python3
"""Verify and aggregate the sealed blind multi-structure Protein panels.

Every prediction and panel seal is verified before any experimental coordinate
file is opened.  Targets enter only at the post-seal comparison boundary.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculate_tm import compute_tm, kabsch, parse_ca  # noqa: E402
from verify.evaluate_sealed_transfer_material_panel_v2 import (  # noqa: E402
    observed_chain,
    unique_author_number_projection,
)


PANELS = (
    {
        "panel": "one-extension-v1",
        "registration": "verify/protein_blind_material_one_extension_registration_20260722.json",
        "run_directory": "verify/development_runs/protein_blind_material_one_extension_20260722",
        "target_directory": "verify/targets/protein_blind_material_one_extension_20260722",
    },
    {
        "panel": "one-extension-v2",
        "registration": "verify/protein_blind_material_one_extension_v2_registration_20260722.json",
        "run_directory": "verify/development_runs/protein_blind_material_one_extension_v2_20260722",
        "target_directory": "verify/targets/protein_blind_material_one_extension_v2_20260722",
    },
    {
        "panel": "published-material-independent-structures",
        "registration": "verify/protein_blind_published_material_panel_registration_20260722.json",
        "run_directory": "verify/development_runs/protein_blind_published_material_panel_20260722",
        "target_directory": "verify/targets/protein_blind_published_material_panel_20260722",
    },
    {
        "panel": "published-material-replication-2",
        "registration": "verify/protein_blind_published_material_replication2_registration_20260722.json",
        "run_directory": "verify/development_runs/protein_blind_published_material_replication2_20260722",
        "target_directory": "verify/targets/protein_blind_published_material_replication2_20260722",
    },
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def verify_panel_before_target_access(specification: dict) -> tuple[dict, dict, Path]:
    registration_path = ROOT / specification["registration"]
    run_directory = ROOT / specification["run_directory"]
    registration_raw = registration_path.read_bytes()
    registration = json.loads(registration_raw)
    panel_seal = json.loads((run_directory / "panel_seal.json").read_text())
    if registration.get("blind_prediction") is not True:
        raise RuntimeError(f"panel is not registered blind: {specification['panel']}")
    if registration.get("target_accesses_before_seal") != 0:
        raise RuntimeError(f"non-zero registered target access: {specification['panel']}")
    if panel_seal.get("blind_prediction") is not True:
        raise RuntimeError(f"panel seal is not blind: {specification['panel']}")
    if panel_seal.get("target_accesses_before_seal") != 0:
        raise RuntimeError(f"non-zero sealed target access: {specification['panel']}")
    if panel_seal.get("panel_registration_sha256") != sha256(registration_raw).hexdigest():
        raise RuntimeError(f"registration drift: {specification['panel']}")
    registered = {row["protein_id"]: row for row in registration["proteins"]}
    sealed = {row["protein_id"]: row for row in panel_seal["runs"]}
    if registered.keys() != sealed.keys():
        raise RuntimeError(f"panel coverage drift: {specification['panel']}")
    for protein_id, row in sealed.items():
        nested = run_directory / protein_id
        nested_seal_path = nested / "seal.json"
        nested_seal = json.loads(nested_seal_path.read_text())
        if nested_seal.get("blind_prediction") is not True:
            raise RuntimeError(f"nested seal is not blind: {protein_id}")
        if nested_seal.get("target_accesses") != 0:
            raise RuntimeError(f"nested target access is non-zero: {protein_id}")
        if digest(nested / "prediction.pdb") != row["prediction_pdb_sha256"]:
            raise RuntimeError(f"prediction drift: {protein_id}")
        if digest(nested / "selected_states.json") != row["selected_states_sha256"]:
            raise RuntimeError(f"state drift: {protein_id}")
        if digest(nested_seal_path) != row["nested_seal_sha256"]:
            raise RuntimeError(f"nested-seal drift: {protein_id}")
    return registration, panel_seal, run_directory


def aligned_errors(prediction: np.ndarray, target: np.ndarray) -> np.ndarray:
    prediction_centered = prediction - np.mean(prediction, axis=0)
    target_centered = target - np.mean(target, axis=0)
    rotation = kabsch(prediction_centered, target_centered)
    return np.linalg.norm(prediction_centered @ rotation - target_centered, axis=1)


def evaluate(output_path: Path) -> dict:
    verified = []
    for specification in PANELS:
        registration, panel_seal, run_directory = verify_panel_before_target_access(
            specification
        )
        verified.append((specification, registration, panel_seal, run_directory))

    results = []
    panel_receipts = []
    for specification, registration, panel_seal, run_directory in verified:
        target_directory = ROOT / specification["target_directory"]
        panel_receipts.append({
            "panel": specification["panel"],
            "registration": specification["registration"],
            "registration_sha256": digest(ROOT / specification["registration"]),
            "panel_seal": f"{specification['run_directory']}/panel_seal.json",
            "panel_seal_sha256": digest(run_directory / "panel_seal.json"),
            "prediction_count": panel_seal["prediction_count"],
            "target_accesses_before_seal": panel_seal["target_accesses_before_seal"],
        })
        for protein in registration["proteins"]:
            future_target = protein["future_target"]
            target_path = target_directory / f"{future_target['pdb_id'].lower()}.pdb"
            observed = observed_chain(
                target_path,
                future_target["chain_id"],
                future_target["model_index"],
            )
            author_number_offset, indices = unique_author_number_projection(
                protein["sequence"], observed
            )
            complete_prediction = parse_ca(
                str(run_directory / protein["protein_id"] / "prediction.pdb")
            )
            prediction = complete_prediction[indices]
            target = np.asarray([row["coordinate"] for row in observed])
            errors = aligned_errors(prediction, target)
            retained = max(1, int(math.ceil(0.95 * len(errors))))
            prediction_distances = np.linalg.norm(
                prediction[:, None, :] - prediction[None, :, :], axis=2
            )
            target_distances = np.linalg.norm(
                target[:, None, :] - target[None, :, :], axis=2
            )
            results.append({
                "panel": specification["panel"],
                "protein_id": protein["protein_id"],
                "pdb_id": future_target["pdb_id"],
                "chain_id": future_target["chain_id"],
                "model_index": future_target["model_index"],
                "sequence_length": len(protein["sequence"]),
                "observed_ca_atoms": len(observed),
                "coverage_fraction": len(observed) / len(protein["sequence"]),
                "author_number_offset": author_number_offset,
                "prediction_pdb_sha256": digest(
                    run_directory / protein["protein_id"] / "prediction.pdb"
                ),
                "target_sha256": digest(target_path),
                "tm_repo": float(compute_tm(prediction, target)),
                "ca_drmsd_angstrom": float(np.sqrt(np.mean(
                    (prediction_distances - target_distances) ** 2
                ))),
                "kabsch_ca_rmsd_angstrom": float(np.sqrt(np.mean(errors ** 2))),
                "ca_rmsd95_angstrom": float(np.sqrt(np.mean(
                    np.sort(errors)[:retained] ** 2
                ))),
            })

    tm_values = np.asarray([row["tm_repo"] for row in results])
    drmsd_values = np.asarray([row["ca_drmsd_angstrom"] for row in results])
    rmsd_values = np.asarray([row["kabsch_ca_rmsd_angstrom"] for row in results])
    rmsd95_values = np.asarray([row["ca_rmsd95_angstrom"] for row in results])
    alphafold_median_rmsd95 = 0.96
    report = {
        "schema": "fold-protein-blind-multi-structure-evidence/v1",
        "status": "completed",
        "result_type": "author-declared blind multi-structure study result",
        "blind_prediction": True,
        "target_accesses_before_all_seals": 0,
        "prediction_count": len(results),
        "distinct_registered_sequence_count": len({
            protein["sequence"]
            for _, registration, _, _ in verified
            for protein in registration["proteins"]
        }),
        "panels": panel_receipts,
        "results": results,
        "aggregate": {
            "median_tm_repo": float(np.median(tm_values)),
            "mean_tm_repo": float(np.mean(tm_values)),
            "maximum_tm_repo": float(np.max(tm_values)),
            "minimum_tm_repo": float(np.min(tm_values)),
            "tm_repo_at_least_0_90_count": int(np.sum(tm_values >= 0.90)),
            "tm_repo_at_least_0_95_count": int(np.sum(tm_values >= 0.95)),
            "median_ca_drmsd_angstrom": float(np.median(drmsd_values)),
            "mean_ca_drmsd_angstrom": float(np.mean(drmsd_values)),
            "median_kabsch_ca_rmsd_angstrom": float(np.median(rmsd_values)),
            "median_ca_rmsd95_angstrom": float(np.median(rmsd95_values)),
            "mean_ca_rmsd95_angstrom": float(np.mean(rmsd95_values)),
            "alphafold_casp14_reported_median_ca_rmsd95_angstrom": alphafold_median_rmsd95,
            "rows_at_or_below_alphafold_reported_median_ca_rmsd95": int(np.sum(
                rmsd95_values <= alphafold_median_rmsd95
            )),
        },
        "comparison_definition": {
            "source": "Jumper et al. (2021), Nature 596, 583-589",
            "alphafold_casp14_reported_median": "0.96 A C-alpha RMSD at 95% residue coverage",
            "fold_protein_measure": "Kabsch-aligned C-alpha RMSD over the lowest-error 95% of correctly mapped observed residues",
            "scope": "24 pre-registered experimental structures covering the 76-residue ubiquitin sequence and its one-residue extension",
        },
        "author_audit": {
            "author": "OpenAI Codex",
            "model": "GPT-5",
            "reasoning_level": "high",
        },
    }
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    report = evaluate(arguments.output.resolve())
    print(json.dumps(report["aggregate"], sort_keys=True))
