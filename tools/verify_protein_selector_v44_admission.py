#!/usr/bin/env python3
"""Verify V44 source binding and complete fixed-point-frontier admission."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v44_admission():
    receipt = json.loads(
        (ROOT / "verify/protein_selector_v44_admission_v1.json").read_text()
    )
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V44 source drift: {relative}")
    construction = receipt["complete_construction"]
    if (construction["connected_parent_count"] != 3
            or construction["paired_state_count"] != 576
            or construction["cycle_rank_target"] != 1
            or construction["causal_direction"] != "n_to_c"):
        raise RuntimeError("V44 construction registration drifted")
    return {
        "schema": "fold-protein-selector-v44-admission-verification/v1",
        "status": "verified",
        **construction,
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v44_admission(), sort_keys=True))
