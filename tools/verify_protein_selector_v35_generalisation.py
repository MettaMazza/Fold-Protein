#!/usr/bin/env python3
"""Verify the source-bound V35 paired-panel structural evidence."""
from __future__ import annotations

import json
from pathlib import Path

from tools.run_blind_panel_v35 import ROOT, sha256_file
from tools.verify_blind_panel_v35 import verify_panel


PANEL = ROOT / "verify/development_runs/protein_v35_generalisation_panel_20260721"
EVIDENCE = ROOT / "verify/protein_selector_v35_generalisation_evidence_v1.json"
TARGET_MAP = ROOT / "verify/protein_v35_generalisation_panel_targets_20260721.json"


def verify_generalisation() -> dict:
    panel = verify_panel(PANEL)
    evidence = json.loads(EVIDENCE.read_text())
    evaluation = json.loads((PANEL / "panel_evaluation.json").read_text())
    if (evidence.get("schema") != "fold-protein-selector-v35-generalisation-evidence/v1"
            or evidence.get("status") != "completed"
            or evidence.get("official_run") is not False):
        raise RuntimeError("invalid V35 generalisation evidence")
    for relative, expected in evidence["source_sha256"].items():
        if sha256_file(ROOT / relative) != expected:
            raise RuntimeError(f"V35 generalisation source drift: {relative}")
    bindings = {
        "panel_registration_sha256": panel["panel_registration_sha256"],
        "panel_seal_sha256": panel["panel_seal_sha256"],
        "panel_evaluation_sha256": sha256_file(PANEL / "panel_evaluation.json"),
        "target_map_sha256": sha256_file(TARGET_MAP),
    }
    for field, actual in bindings.items():
        if evidence["panel"].get(field) != actual:
            raise RuntimeError(f"V35 generalisation binding drift: {field}")

    for protein_id, protein in evidence["proteins"].items():
        evaluated = evaluation["by_protein"][protein_id]
        for version in ("v34", "v35"):
            directory = PANEL / protein_id / version
            row = protein[version]
            file_bindings = {
                "seal_sha256": sha256_file(directory / "seal.json"),
                "selected_states_sha256": sha256_file(directory / "selected_states.json"),
                "prediction_pdb_sha256": sha256_file(directory / "prediction.pdb"),
                "evaluation_sha256": sha256_file(directory / "evaluation.json"),
            }
            for field, actual in file_bindings.items():
                if row.get(field) != actual:
                    raise RuntimeError(
                        f"V35 generalisation artifact drift: {protein_id} {version} {field}")
            if (row["tm_score"] != evaluated[version]["tm_score"]
                    or row["ca_drmsd_angstrom"]
                    != evaluated[version]["ca_drmsd_angstrom"]):
                raise RuntimeError(f"V35 generalisation score drift: {protein_id} {version}")

    aggregate = evidence["aggregate"]
    if (aggregate["proteins_with_tm_improvement"] != 2
            or aggregate["proteins_with_ca_drmsd_improvement"] != 2
            or evaluation["aggregate"]["v35_minus_v34"][
                "proteins_with_tm_improvement"] != 2
            or evaluation["aggregate"]["v35_minus_v34"][
                "proteins_with_drmsd_improvement"] != 2):
        raise RuntimeError("V35 cross-protein improvement census drift")
    return {
        "schema": "fold-protein-selector-v35-generalisation-verification/v1",
        "status": "verified",
        "verified_predictions": panel["verified_predictions"],
        "proteins_with_tm_improvement": 2,
        "proteins_with_ca_drmsd_improvement": 2,
        "v35_mean_tm_score": aggregate["v35_mean_tm_score"],
        "v35_mean_ca_drmsd_angstrom": aggregate["v35_mean_ca_drmsd_angstrom"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_generalisation(), sort_keys=True))
