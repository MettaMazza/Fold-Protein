#!/usr/bin/env python3
"""Evaluate the paired panel only after all V34/V35 predictions verify."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculate_tm import compute_tm, parse_ca  # noqa: E402
from tools.verify_blind_panel_v35 import verify_panel  # noqa: E402


THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_chain(path: Path, chain_id: str, model_index: int) -> tuple[str, np.ndarray]:
    sequence = []
    coordinates = []
    seen = set()
    current_model = 1
    saw_models = False
    for line in path.read_text().splitlines():
        if line.startswith("MODEL"):
            saw_models = True
            current_model = int(line[10:14])
            continue
        if line.startswith("ENDMDL") and current_model == model_index:
            break
        if not line.startswith("ATOM") or line[12:16].strip() != "CA":
            continue
        active_model = current_model if saw_models else 1
        if active_model != model_index or line[21].strip() != chain_id:
            continue
        identity = (line[22:26].strip(), line[26])
        if identity in seen:
            continue
        seen.add(identity)
        residue = line[17:20].strip()
        if residue not in THREE_TO_ONE:
            raise RuntimeError(f"unsupported target residue: {residue}")
        sequence.append(THREE_TO_ONE[residue])
        coordinates.append([
            float(line[30:38]), float(line[38:46]), float(line[46:54])])
    if not coordinates:
        raise RuntimeError(f"no target C-alpha atoms for model {model_index} chain {chain_id}")
    return "".join(sequence), np.asarray(coordinates)


def evaluate_panel(panel_dir: Path, target_map_path: Path) -> dict:
    panel_dir, target_map_path = map(Path.resolve, (panel_dir, target_map_path))

    # This complete verification is deliberately before the target map is read.
    verification = verify_panel(panel_dir)
    target_map = json.loads(target_map_path.read_text())
    if set(target_map) != {
        "schema", "result_type", "official_run", "panel_registration_sha256", "targets"
    } or target_map["schema"] != "fold-protein-v35-paired-panel-target-map/v1":
        raise ValueError("unsupported paired-panel target map")
    if target_map["official_run"] is not False:
        raise ValueError("only Maria may register an official run")
    if target_map["panel_registration_sha256"] != verification["panel_registration_sha256"]:
        raise RuntimeError("target map is not bound to the sealed panel registration")

    registration = json.loads((panel_dir / "panel_registration.json").read_text())
    proteins = {row["protein_id"]: row for row in registration["proteins"]}
    targets = {row["protein_id"]: row for row in target_map["targets"]}
    if set(targets) != set(proteins):
        raise RuntimeError("target-map coverage differs from the sealed protein panel")
    if (panel_dir / "panel_evaluation.json").exists():
        raise FileExistsError(panel_dir / "panel_evaluation.json")

    evaluations = []
    for protein_id, protein in proteins.items():
        target_row = targets[protein_id]
        if set(target_row) != {
            "protein_id", "target", "target_sha256", "model_index", "chain_id"
        }:
            raise ValueError(f"invalid target row: {protein_id}")
        target_path = ROOT / target_row["target"]
        if sha256(target_path) != target_row["target_sha256"]:
            raise RuntimeError(f"target drift: {protein_id}")
        target_sequence, target_coordinates = target_chain(
            target_path, target_row["chain_id"], target_row["model_index"])
        if target_sequence != protein["sequence"]:
            raise RuntimeError(f"registered sequence differs from target chain: {protein_id}")

        for version in ("v34", "v35"):
            nested_dir = panel_dir / protein_id / version
            states = json.loads((nested_dir / "selected_states.json").read_text())
            if states["sequence"] != target_sequence:
                raise RuntimeError(f"sealed sequence differs from target chain: {protein_id} {version}")
            prediction = parse_ca(str(nested_dir / "prediction.pdb"))
            if len(prediction) != len(target_coordinates):
                raise RuntimeError(f"C-alpha count mismatch: {protein_id} {version}")
            pred_dist = np.linalg.norm(
                prediction[:, None, :] - prediction[None, :, :], axis=2)
            target_dist = np.linalg.norm(
                target_coordinates[:, None, :] - target_coordinates[None, :, :], axis=2)
            evidence = {
                "schema": f"fold-protein-blind-evaluation/{version}-paired-panel",
                "status": "completed",
                "result_type": "cumulative development benchmark",
                "official_run": False,
                "protein_id": protein_id,
                "run_id": states["run_id"],
                "execution": "post-panel-seal structural comparison",
                "panel_seal_sha256": verification["panel_seal_sha256"],
                "nested_seal_sha256": sha256(nested_dir / "seal.json"),
                "target_id": target_path.name,
                "target_sha256": target_row["target_sha256"],
                "target_projection": {
                    "model_index": target_row["model_index"],
                    "chain_id": target_row["chain_id"],
                },
                "matched_ca_atoms": len(prediction),
                "sequence_length": len(target_sequence),
                "tm_score": float(compute_tm(prediction, target_coordinates)),
                "ca_drmsd_angstrom": float(np.sqrt(np.mean(
                    (pred_dist - target_dist) ** 2))),
                "mode_census": {
                    mode: states["modes"].count(mode)
                    for mode in sorted(set(states["modes"]))
                },
            }
            output_path = nested_dir / "evaluation.json"
            if output_path.exists():
                raise FileExistsError(output_path)
            output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
            evaluations.append(evidence)

    by_protein = {}
    for protein_id in proteins:
        pair = {
            row["schema"].split("/")[1].split("-")[0]: row
            for row in evaluations if row["protein_id"] == protein_id
        }
        v34, v35 = pair["v34"], pair["v35"]
        tm_delta = v35["tm_score"] - v34["tm_score"]
        drmsd_reduction = v34["ca_drmsd_angstrom"] - v35["ca_drmsd_angstrom"]
        by_protein[protein_id] = {
            "v34": {
                "tm_score": v34["tm_score"],
                "ca_drmsd_angstrom": v34["ca_drmsd_angstrom"],
            },
            "v35": {
                "tm_score": v35["tm_score"],
                "ca_drmsd_angstrom": v35["ca_drmsd_angstrom"],
            },
            "v35_minus_v34": {
                "tm_score_absolute": tm_delta,
                "tm_score_percent": 100.0 * tm_delta / v34["tm_score"],
                "ca_drmsd_reduction_angstrom": drmsd_reduction,
                "ca_drmsd_performance_percent": (
                    100.0 * drmsd_reduction / v34["ca_drmsd_angstrom"]),
            },
        }

    aggregate = {}
    for version in ("v34", "v35"):
        rows = [row for row in evaluations if f"/{version}-" in row["schema"]]
        aggregate[version] = {
            "mean_tm_score": sum(row["tm_score"] for row in rows) / len(rows),
            "mean_ca_drmsd_angstrom": (
                sum(row["ca_drmsd_angstrom"] for row in rows) / len(rows)),
        }
    aggregate["v35_minus_v34"] = {
        "mean_tm_score_absolute": (
            aggregate["v35"]["mean_tm_score"] - aggregate["v34"]["mean_tm_score"]),
        "mean_ca_drmsd_reduction_angstrom": (
            aggregate["v34"]["mean_ca_drmsd_angstrom"]
            - aggregate["v35"]["mean_ca_drmsd_angstrom"]),
        "proteins_with_tm_improvement": sum(
            row["v35_minus_v34"]["tm_score_absolute"] > 0
            for row in by_protein.values()),
        "proteins_with_drmsd_improvement": sum(
            row["v35_minus_v34"]["ca_drmsd_reduction_angstrom"] > 0
            for row in by_protein.values()),
    }
    report = {
        "schema": "fold-protein-v35-paired-panel-evaluation/v1",
        "status": "completed",
        "result_type": "cumulative development benchmark",
        "official_run": False,
        "panel_id": verification["panel_id"],
        "panel_registration_sha256": verification["panel_registration_sha256"],
        "panel_seal_sha256": verification["panel_seal_sha256"],
        "target_map_sha256": sha256(target_map_path),
        "protein_count": len(proteins),
        "prediction_count": len(evaluations),
        "by_protein": by_protein,
        "aggregate": aggregate,
    }
    (panel_dir / "panel_evaluation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("panel_dir", type=Path)
    parser.add_argument("target_map", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_panel(args.panel_dir, args.target_map), sort_keys=True))


if __name__ == "__main__":
    main()
