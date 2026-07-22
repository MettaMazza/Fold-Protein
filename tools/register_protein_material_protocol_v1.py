#!/usr/bin/env python3
"""Source-bind the admitted protein material protocol and L76 input."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verify/protein_material_protocol_v1.json"
INPUT = ROOT / "verify/development_inputs/ubiquitin_material_v1_l76_20260721.json"
RELATION = ROOT / "verify/protein_material_relation_v1.json"
ADMISSION = ROOT / "verify/protein_material_architecture_v1_admission.json"
RUNTIME_SOURCES = (
    "tools/protein_material_architecture_v1.py",
    "tools/run_protein_material_protocol_v1.py",
    "tools/protein_backbone_geometry_v1.py",
    "tools/blind_24_lattice_selector_v3.py",
    "tools/residue_partition_v1.py",
    "verify/protein_material_relation_v1.json",
    "verify/protein_material_architecture_v1_admission.json",
    "constants/protein_material_architecture_v1_admission.ep",
    "tests/test_protein_material_architecture_v1_admission.ep",
)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main():
    relation = json.loads(RELATION.read_text())
    admission = json.loads(ADMISSION.read_text())
    if relation.get("status") != "derived" or admission.get("status") != "admitted":
        raise RuntimeError("material relation/admission is incomplete")
    manifest = {
        "schema": "fold-protein-material-protocol/v1",
        "status": "registered",
        "result_type": "cumulative development benchmark protocol",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "execution": (
            "complete 576-state domain at every residue; exact material-frame "
            "matching; SFT colour-window/binary-overlap/One-advance closure; "
            "canonical terminal gauge; direct unique structure emission"
        ),
        "material_relation": str(RELATION.relative_to(ROOT)),
        "material_relation_sha256": file_sha256(RELATION),
        "admission_receipt": str(ADMISSION.relative_to(ROOT)),
        "admission_receipt_sha256": file_sha256(ADMISSION),
        "runtime_prohibitions": [
            "experimental target coordinates",
            "protected witness file access",
            "comparison scores",
            "candidate ordering",
            "weights",
            "fitted parameters",
            "reward",
        ],
        "source_sha256": {
            relative: file_sha256(ROOT / relative)
            for relative in RUNTIME_SOURCES
        },
        "author_audit": {
            "author": "OpenAI Codex",
            "model": "GPT-5",
            "reasoning_level": "high",
        },
    }
    selector_input = {
        "run_id": "ubiquitin-material-v1-complete-domain-l76-20260721-r2",
        "sequence": relation["sequence"],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    INPUT.parent.mkdir(parents=True, exist_ok=True)
    INPUT.write_text(json.dumps(selector_input, separators=(",", ":")) + "\n")
    print(json.dumps({
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": file_sha256(MANIFEST),
        "input": str(INPUT.relative_to(ROOT)),
        "input_sha256": file_sha256(INPUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
