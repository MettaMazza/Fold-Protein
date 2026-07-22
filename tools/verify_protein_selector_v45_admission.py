#!/usr/bin/env python3
"""Verify V45 source binding and complete boundary-axis admission."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v45_admission():
    receipt = json.loads(
        (ROOT / "verify/protein_selector_v45_admission_v1.json").read_text()
    )
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V45 source drift: {relative}")
    construction = receipt["complete_construction"]
    if (construction["connected_parent_count"] != 3
            or construction["axis_value_count"] != 24
            or construction["descent_order_count"] != 4
            or construction["fixed_point_trace_count"] != 12
            or construction["cycle_rank_target"] != 1):
        raise RuntimeError("V45 construction registration drifted")
    return {
        "schema": "fold-protein-selector-v45-admission-verification/v1",
        "status": "verified",
        **construction,
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v45_admission(), sort_keys=True))
