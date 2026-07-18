#!/usr/bin/env python3
"""Trace exact selector-v2 ancestry as a sealed sequence-only relation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from tools.blind_24_lattice_selector_v2 import (
        SelectorV2Config, _candidate_key)
    from tools.blind_24_lattice_solver import active_candidates
    from tools.verify_blind_length_ladder_v2 import verify_ladder
except ImportError:
    from blind_24_lattice_selector_v2 import SelectorV2Config, _candidate_key
    from blind_24_lattice_solver import active_candidates
    from verify_blind_length_ladder_v2 import verify_ladder


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descendant_status(beam: list[tuple[tuple, tuple]], anchor: tuple) -> dict:
    descendants = [
        (rank, key, path) for rank, (key, path) in enumerate(beam, 1)
        if path[:len(anchor)] == anchor
    ]
    if not descendants:
        return {"retained_descendants": 0, "best_rank": None,
                "best_key": None, "lineage_alive": False}
    rank, key, _ = descendants[0]
    return {"retained_descendants": len(descendants), "best_rank": rank,
            "best_key": list(key), "lineage_alive": True}


def trace_registered_lineages(sequence: str, specifications: list[dict],
                             config: SelectorV2Config | None = None) -> list[dict]:
    """Replay one maximum-length beam and trace every registered prefix anchor.

    The selector key at active state ``i`` consumes only ``sequence[:i+2]``.
    Therefore every registered run sharing that prefix has the identical beam at
    that frontier. One maximum-length replay is the exact common computation;
    repeating it once per pair adds no information.
    """
    config = config or SelectorV2Config()
    trackers = []
    for specification in specifications:
        anchor = tuple(specification["anchor"])
        anchor_active_length = len(anchor)
        long_active_length = specification["long_length"] - 1
        if anchor_active_length < 1 or long_active_length >= len(sequence):
            raise ValueError("registered lineage bounds are outside the maximum sequence")
        trackers.append({
            **specification,
            "anchor": anchor,
            "anchor_active_length": anchor_active_length,
            "long_active_length": long_active_length,
            "anchor_verified": False,
            "rows": [],
            "final_descends": None,
        })
    beam = [((0, 1.0, 0.0), tuple())]
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                expanded.append((_candidate_key(sequence, list(candidate)), candidate))
        expanded.sort(key=lambda item: (item[0], item[1]))
        beam = expanded[:config.beam_width]
        active_length = index + 1
        for tracker in trackers:
            if active_length == tracker["anchor_active_length"]:
                if beam[0][1] != tracker["anchor"]:
                    raise RuntimeError(
                        "registered shorter winner differs from replayed frontier"
                    )
                tracker["anchor_verified"] = True
            elif (tracker["anchor_active_length"] < active_length
                  <= tracker["long_active_length"]):
                status = descendant_status(beam, tracker["anchor"])
                tracker["rows"].append({
                    "active_state": index,
                    "residue": sequence[index],
                    **status,
                })
            if active_length == tracker["long_active_length"]:
                tracker["final_descends"] = (
                    beam[0][1][:len(tracker["anchor"])] == tracker["anchor"]
                )

    output = []
    for tracker in trackers:
        if not tracker["anchor_verified"]:
            raise RuntimeError("anchor frontier was not reached")
        rows = tracker["rows"]
        output.append({
            "short_length": tracker["short_length"],
            "long_length": tracker["long_length"],
            "anchor_active_length": tracker["anchor_active_length"],
            "anchor_path": list(tracker["anchor"]),
            "anchor_verified_as_frontier_winner": True,
            "continuation_rows": rows,
            "first_displaced_active_state": next(
                (row["active_state"] for row in rows
                 if row["best_rank"] not in (None, 1)), None
            ),
            "first_extinct_active_state": next(
                (row["active_state"] for row in rows
                 if not row["lineage_alive"]), None
            ),
            "final_path_descends_from_anchor": tracker["final_descends"],
        })
    return output


def trace(directory: Path, output: Path) -> dict:
    directory = directory.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"continuation-lineage receipt already exists: {output}")
    verification = verify_ladder(directory)
    seal_path = directory / "ladder_seal.json"
    seal = json.loads(seal_path.read_text())
    records = []
    bindings = []
    for binding in seal["runs"]:
        if binding["status"] != "completed":
            continue
        path = directory / binding["run_id"] / "selected_states.json"
        records.append(json.loads(path.read_text()))
        bindings.append({"length": binding["length"], "sha256": sha256(path)})
    specifications = []
    for short, long in zip(records, records[1:]):
        if not long["sequence"].startswith(short["sequence"]):
            raise RuntimeError("registered longer sequence is not a continuation")
        specifications.append({
            "anchor": short["states"][:-1],
            "short_length": len(short["sequence"]),
            "long_length": len(long["sequence"]),
        })
    comparisons = trace_registered_lineages(records[-1]["sequence"], specifications)
    record = {
        "schema": "fold-protein-selector-v2-continuation-lineage/v1",
        "status": "completed",
        "result_type": "measured implementation result",
        "target_access": "none",
        "governance_authority": False,
        "relation": (
            "a longer path is a descendant exactly when its active-state tuple "
            "begins with the registered shorter winner"
        ),
        "replay_strategy": (
            "one maximum-length replay; every frontier is shared exactly by all "
            "registered runs with the same sequence prefix"
        ),
        "beam_width": SelectorV2Config().beam_width,
        "analyzer": {
            "path": "tools/trace_selector_continuation_lineage_v2.py",
            "sha256": sha256(Path(__file__).resolve()),
        },
        "selector_source_sha256": sha256(
            Path(__file__).resolve().parent / "blind_24_lattice_selector_v2.py"),
        "verified_ladder": verification,
        "selected_state_bindings": bindings,
        "comparisons": comparisons,
        "interpretation": (
            "sequence-only continuation lineage; the engine determines forcing "
            "or halt and Maria Smith assigns project conclusions"
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
    print(json.dumps(trace(args.directory, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
