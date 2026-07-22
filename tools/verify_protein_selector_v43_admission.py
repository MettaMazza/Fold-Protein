#!/usr/bin/env python3
"""Verify V43 source binding and complete One-cycle-frontier admission."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selector_v43_admission():
    receipt = json.loads(
        (ROOT / "verify/protein_selector_v43_admission_v1.json").read_text()
    )
    for relative, expected in receipt["source_sha256"].items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"V43 source drift: {relative}")
    frontier = receipt["complete_frontier"]
    if (frontier["cycle_rank_target"] != 1
            or frontier["parent_cube_count"] != 8192
            or frontier["count"] != 1082):
        raise RuntimeError("V43 frontier registration drifted")
    return {
        "schema": "fold-protein-selector-v43-admission-verification/v1",
        "status": "verified",
        "parent_cube_count": 8192,
        "cycle_rank_target": 1,
        "one_cycle_frontier_count": 1082,
    }


if __name__ == "__main__":
    print(json.dumps(verify_selector_v43_admission(), sort_keys=True))
