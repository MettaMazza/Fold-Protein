#!/usr/bin/env python3
"""Trace selector-v2 prefix changes through its own target-free relations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from tools.blind_24_lattice_selector_v2 import _candidate_key
    from tools.blind_24_lattice_solver import angles_for_state
    from tools.verify_blind_length_ladder_v2 import verify_ladder
except ImportError:
    from blind_24_lattice_selector_v2 import _candidate_key
    from blind_24_lattice_solver import angles_for_state
    from verify_blind_length_ladder_v2 import verify_ladder


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relation(left: tuple, right: tuple) -> str:
    if left < right:
        return "shorter-path-prefix-first"
    if right < left:
        return "longer-path-prefix-first"
    return "equal-topology-key"


def trace_pair(short: dict, long: dict) -> dict:
    short_sequence = short["sequence"]
    long_sequence = long["sequence"]
    if not long_sequence.startswith(short_sequence):
        raise ValueError("long sequence does not extend short sequence")
    short_states = short["states"]
    long_states = long["states"]
    if len(short_states) != len(short_sequence) or \
            len(long_states) != len(long_sequence):
        raise ValueError("state path length does not match sequence length")
    active = max(0, len(short_states) - 1)
    changed = []
    for index in range(active):
        if short_states[index] == long_states[index]:
            continue
        short_prefix = short_states[:index + 1]
        long_prefix = long_states[:index + 1]
        short_key = tuple(_candidate_key(short_sequence, short_prefix))
        long_key = tuple(_candidate_key(short_sequence, long_prefix))
        short_selection_key = (short_key, tuple(short_prefix))
        long_selection_key = (long_key, tuple(long_prefix))
        short_angles = angles_for_state(short_states[index])
        long_angles = angles_for_state(long_states[index])
        changed.append({
            "active_state": index,
            "residue": short_sequence[index],
            "short_state": short_states[index],
            "long_state": long_states[index],
            "short_angles_radians": list(short_angles),
            "long_angles_radians": list(long_angles),
            "short_chosen_prefix_key": list(short_key),
            "long_chosen_prefix_key": list(long_key),
            "topology_key_relation_at_prefix": relation(short_key, long_key),
            "full_selection_relation_at_prefix": relation(
                short_selection_key, long_selection_key),
        })
    short_trace = short.get("score_trace", [])[:active]
    long_trace = long.get("score_trace", [])[:active]
    return {
        "short_length": len(short_sequence),
        "long_length": len(long_sequence),
        "active_states_compared": active,
        "changed_state_count": len(changed),
        "first_divergence_zero_based": changed[0]["active_state"] if changed else None,
        "shared_frontier_trace_identical": short_trace == long_trace,
        "changed_states": changed,
    }


def trace(directory: Path, consistency_path: Path, output: Path) -> dict:
    directory = directory.resolve()
    consistency_path = consistency_path.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"decision-trace receipt already exists: {output}")
    verification = verify_ladder(directory)
    consistency = json.loads(consistency_path.read_text())
    if consistency.get("schema") != \
            "fold-protein-selector-v2-prefix-consistency/v1":
        raise RuntimeError("unsupported prefix-consistency receipt")
    if consistency.get("registration_sha256") != verification["registration_sha256"] or \
            consistency.get("ladder_seal_sha256") != verification["seal_sha256"]:
        raise RuntimeError("prefix-consistency receipt differs from verified ladder")
    seal_path = directory / "ladder_seal.json"
    seal = json.loads(seal_path.read_text())
    runs = []
    bindings = []
    for binding in seal["runs"]:
        if binding["status"] != "completed":
            continue
        path = directory / binding["run_id"] / "selected_states.json"
        runs.append(json.loads(path.read_text()))
        bindings.append({"length": binding["length"], "sha256": sha256(path)})
    comparisons = [trace_pair(short, long) for short, long in zip(runs, runs[1:])]
    for traced, counted in zip(comparisons, consistency["comparisons"]):
        if traced["active_states_compared"] != counted["active_states_compared"] or \
                traced["changed_state_count"] != \
                counted["active_states_compared"] - counted["identical_active_states"] or \
                traced["first_divergence_zero_based"] != \
                counted["first_divergence_zero_based"]:
            raise RuntimeError("decision trace differs from consistency receipt")
    record = {
        "schema": "fold-protein-selector-v2-decision-trace/v1",
        "status": "completed",
        "result_type": "measured implementation result",
        "target_access": "none",
        "governance_authority": False,
        "ordering_relation": ["self-exclusion violations", "hydrophobic dispersion",
                              "compaction", "state-path lexicographic order"],
        "analyzer": {
            "path": "tools/trace_blind_ladder_decisions_v2.py",
            "sha256": sha256(Path(__file__).resolve()),
        },
        "verified_ladder": verification,
        "consistency_receipt_sha256": sha256(consistency_path),
        "selected_state_bindings": bindings,
        "comparisons": comparisons,
        "interpretation": (
            "target-free selector decision trace only; the engine determines "
            "forcing or halt and Maria Smith assigns project conclusions"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("consistency", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(trace(args.directory, args.consistency, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
