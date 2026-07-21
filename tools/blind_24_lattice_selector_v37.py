#!/usr/bin/env python3
"""V37: reconcile V36 by an unordered binary/colour whole-chain census.

V36 supplies all sixteen directional full-chain candidates.  V37 admits no new
candidate or score.  It partitions the active-state count into complete b+c
groups and requires the two closed protein modes to have the unordered census
{b*k, c*k}.  Alpha and beta are deliberately not assigned to either generator.
Exactly one V36 candidate must satisfy the target-incapable relation or runtime
selection halts.
"""
from __future__ import annotations

from collections import Counter

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)
from tools.blind_24_lattice_selector_v34 import closed_angle_domain
from tools.blind_24_lattice_selector_v36 import (
    COMPLETE_CHAIN_CANDIDATES,
    select_state_path_v36,
)


BINARY_COUNT = 2
COLOUR_COUNT = 3
PARTITION_SPAN = BINARY_COUNT + COLOUR_COUNT


def _unordered_mode_census(path: list[int], state_modes: dict[int, str]) -> tuple[int, int]:
    counts = Counter(state_modes[state] for state in path)
    if set(counts) != set(state_modes.values()):
        return tuple(sorted((counts.get("alpha", 0), counts.get("beta", 0))))
    return tuple(sorted(counts.values()))


def select_state_path_v37(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    active_count = len(sequence) - 1
    if active_count % PARTITION_SPAN:
        raise RuntimeError("V37 active chain does not close into binary-colour groups")
    unit_count = active_count // PARTITION_SPAN
    expected_census = tuple(sorted((BINARY_COUNT * unit_count, COLOUR_COUNT * unit_count)))

    complete = select_state_path_v36(sequence)
    candidates = complete["reconciliation_trace"]
    if len(candidates) != COMPLETE_CHAIN_CANDIDATES:
        raise RuntimeError("V37 did not receive the complete V36 grammar")
    domain = closed_angle_domain()
    state_modes = {state: mode for mode, state in domain.items()}
    qualifying = []
    census_trace = []
    for candidate in candidates:
        census = _unordered_mode_census(candidate["path"], state_modes)
        qualifies = census == expected_census
        census_trace.append({
            "direction": candidate["direction"],
            "context": candidate["context"],
            "unordered_mode_census": list(census),
            "qualifies": qualifies,
        })
        if qualifies:
            qualifying.append(candidate)
    if len(qualifying) != 1:
        raise RuntimeError(
            f"V37 requires one generator-partition candidate, found {len(qualifying)}"
        )

    selected = qualifying[0]
    active_path = selected["path"]
    states = active_path + [CANONICAL_STATE]
    modes = [state_modes[state] for state in active_path] + ["inactive"]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "modes": modes,
        "atoms": atoms,
        "closed_domain": domain,
        "complete_chain_candidates": COMPLETE_CHAIN_CANDIDATES,
        "partition_span": PARTITION_SPAN,
        "partition_unit_count": unit_count,
        "expected_unordered_mode_census": list(expected_census),
        "qualifying_candidates": len(qualifying),
        "census_trace": census_trace,
        "selected_direction": selected["direction"],
        "selected_context": selected["context"],
        "final_key": selected["key"],
    }
