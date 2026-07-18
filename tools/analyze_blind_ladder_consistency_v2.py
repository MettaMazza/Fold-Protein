#!/usr/bin/env python3
"""Target-free continuation analysis for a sealed selector-v2 length ladder.

This does not score a protein and never opens a target. It asks one exact
development question: when more sequence becomes available, how many previously
C-alpha-active state decisions remain identical? The output is a measured
implementation receipt, not a project finding or run-authority decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from tools.verify_blind_length_ladder_v2 import verify_ladder
except ImportError:
    from verify_blind_length_ladder_v2 import verify_ladder


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def continuation_rows(runs: list[tuple[int, list[int]]]) -> list[dict]:
    """Compare each prefix with the next registered prefix exactly.

    The final state of a shorter run is canonical because its dihedrals are
    C-alpha inactive. It is excluded from the comparison; every earlier state
    is an active decision and is compared position by position.
    """
    rows = []
    for (short_length, short), (long_length, long) in zip(runs, runs[1:]):
        if len(short) != short_length or len(long) != long_length:
            raise ValueError("state path length does not match registered length")
        active = max(0, short_length - 1)
        matches = sum(1 for index in range(active) if short[index] == long[index])
        first_divergence = next(
            (index for index in range(active) if short[index] != long[index]), None)
        rows.append({
            "short_length": short_length,
            "long_length": long_length,
            "active_states_compared": active,
            "identical_active_states": matches,
            "first_divergence_zero_based": first_divergence,
        })
    return rows


def analyze(directory: Path, output: Path) -> dict:
    directory = directory.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"analysis receipt already exists: {output}")
    verification = verify_ladder(directory)
    registration_path = directory / "ladder_registration.json"
    seal_path = directory / "ladder_seal.json"
    registration = json.loads(registration_path.read_text())
    seal = json.loads(seal_path.read_text())
    runs = []
    bindings = []
    for binding in seal["runs"]:
        if binding["status"] != "completed":
            continue
        run_id = binding["run_id"]
        states_path = directory / run_id / "selected_states.json"
        state_record = json.loads(states_path.read_text())
        runs.append((binding["length"], state_record["states"]))
        bindings.append({
            "length": binding["length"],
            "selected_states_sha256": sha256(states_path),
        })
    rows = continuation_rows(runs)
    record = {
        "schema": "fold-protein-selector-v2-prefix-consistency/v1",
        "status": "completed",
        "result_type": "measured implementation result",
        "target_access": "none",
        "governance_authority": False,
        "analyzer": {
            "path": "tools/analyze_blind_ladder_consistency_v2.py",
            "sha256": sha256(Path(__file__).resolve()),
        },
        "registration_sha256": sha256(registration_path),
        "ladder_seal_sha256": sha256(seal_path),
        "verified_ladder": verification,
        "registered_lengths": registration["lengths"],
        "state_bindings": bindings,
        "comparisons": rows,
        "interpretation": (
            "exact prefix-continuation measurement only; Maria Smith assigns "
            "any project conclusion and decides real blind-run timing"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.directory, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
