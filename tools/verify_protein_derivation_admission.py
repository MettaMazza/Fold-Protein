#!/usr/bin/env python3
"""Enforce the boundary between engine forcing and development evidence."""
from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ADMISSION = ROOT / "verify/protein_derivation_admission_v1.json"
REGISTRY = ROOT / "verify/protein_forcing_registry_v1.json"

ALLOWED_STATUSES = {
    "engine_closed_foundation",
    "engine_closed_protein_relation",
    "named_forward_forcing_constitution",
    "archived_legacy_development",
    "archived_non_admitted_development",
}

FORBIDDEN_CLAIMS = {
    "sequence-forced tertiary": "V29/V30 topology was never engine-closed",
    "V29 derives": "V29 is a non-admitted development architecture",
    "v29 derives": "V29 is a non-admitted development architecture",
    "V30 derives": "V30 is a non-admitted development architecture",
    "v30 derives": "V30 is a non-admitted development architecture",
    "V30 forces": "V30 is a non-admitted development architecture",
    "v30 forces": "V30 is a non-admitted development architecture",
    "V32 derives": "V32 is a non-admitted development architecture",
    "v32 derives": "V32 is a non-admitted development architecture",
    "next architecture derives": "an unimplemented agent proposal cannot be a derivation",
    "next state derives": "an unimplemented agent proposal cannot be a derivation",
    "next representational state derives": "an unimplemented agent proposal cannot be a derivation",
    "next forward-forced state": "an unimplemented agent proposal cannot be forward-forced",
}

CLAIM_SURFACES = (
    ROOT / "AGENT.md",
    ROOT / "README.md",
    ROOT / "verify/PROTEIN_FORCING_AUDIT.md",
    ROOT / "papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md",
    ROOT / "papers/Super_Parity_Zero_Parameter_Protein_Folding.md",
)


def selector_manifests() -> set[str]:
    manifests = set()
    for path in (ROOT / "verify").glob("blind_selector_v*.json"):
        match = re.fullmatch(r"blind_selector_v(\d+)(?:_(\d+))?\.json", path.name)
        if match:
            manifests.add(path.stem)
    return manifests


def verify_admission() -> dict:
    admission = json.loads(ADMISSION.read_text())
    registry = json.loads(REGISTRY.read_text())
    if admission.get("schema") != "fold-protein-derivation-admission/v1":
        raise RuntimeError("unsupported protein derivation admission schema")

    statuses = {
        item["status"]
        for section in ("admitted_relations", "archived_development")
        for item in admission[section].values()
    }
    unexpected = statuses - ALLOWED_STATUSES
    if unexpected:
        raise RuntimeError(f"unknown derivation admission statuses: {sorted(unexpected)}")

    required = admission.get("required_derivation_guards", [])
    if len(required) != 7 or len(set(required)) != 7:
        raise RuntimeError("the complete seven-part derivation guard is not registered")

    expected_manifests = {"blind_selector_v1", "blind_selector_v2", "blind_selector_v3"}
    expected_manifests.update(
        path.stem for path in (ROOT / "verify").glob("blind_selector_v*.json")
        if re.fullmatch(r"blind_selector_v(?:[4-9]|[12]\d|3[0-3])(?:_\d+)?\.json", path.name)
    )
    expected_manifests.add("blind_selector_v34")
    expected_manifests.add("blind_selector_v35")
    actual_manifests = selector_manifests()
    if actual_manifests != expected_manifests:
        raise RuntimeError(
            "selector admission coverage changed; "
            f"missing={sorted(actual_manifests - expected_manifests)}; "
            f"unexpected={sorted(expected_manifests - actual_manifests)}"
        )

    class_names = set(registry["classes"])
    for section in ("admitted_relations", "archived_development"):
        for name, item in admission[section].items():
            source_class = item.get("source_class")
            if source_class and source_class not in class_names:
                raise RuntimeError(f"{name} names missing source class {source_class}")

    interpretation = registry.get("route_status_interpretation", "")
    if "Every blind_selector_v4 through blind_selector_v33" not in interpretation:
        raise RuntimeError("V4-V33 route-status interpretation is not explicit")
    if "archived non-admitted" not in interpretation:
        raise RuntimeError("V4-V33 are not explicitly excluded from active admission")

    active = set(registry["legacy_exclusion"]["promoted_or_active_classes"])
    allowed_active = {
        "engine_foundation_trace",
        "protein_engine_closed_relations",
        "protected_target_assisted_forward_forcing",
        "blind_v3_named_forward_forcing_development",
        "blind_v34_closed_domain_forward_forcing",
        "blind_v35_complete_boundary_forward_forcing",
    }
    if active != allowed_active:
        raise RuntimeError(
            "active admission contains an unclosed or historical class; "
            f"actual={sorted(active)} expected={sorted(allowed_active)}"
        )

    violations = []
    for path in CLAIM_SURFACES:
        text = path.read_text()
        for phrase, reason in FORBIDDEN_CLAIMS.items():
            if phrase in text:
                violations.append(f"{path.relative_to(ROOT)}: {phrase}: {reason}")
    if violations:
        raise RuntimeError("unclosed forcing claims remain: " + "; ".join(violations))

    return {
        "schema": "fold-protein-derivation-admission-verification/v1",
        "status": "verified",
        "selector_manifests_classified": len(actual_manifests),
        "active_classes": sorted(active),
        "archived_selector_range": "V4-V33 non-admitted development evidence",
        "required_derivation_guards": len(required),
    }


if __name__ == "__main__":
    print(json.dumps(verify_admission(), sort_keys=True))
