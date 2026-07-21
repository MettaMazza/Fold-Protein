#!/usr/bin/env python3
"""V36: reconcile complete V35 context frontiers from both chain boundaries.

The linear chain has two boundaries. Each boundary propagates the complete
eight-context V35 graph, generating exactly sixteen directional full-chain
candidates. The already-admitted V3 total order and deterministic path tie-break
then resolve the complete set. No new score, beam, parameter, cutoff or target
enters the reconciliation.
"""
from __future__ import annotations

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    _candidate_key,
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)
from tools.blind_24_lattice_selector_v34 import closed_angle_domain
from tools.blind_24_lattice_selector_v35 import (
    BOUNDARY_CONTEXTS,
    BOUNDARY_RESIDUES,
    QUARTET_TRANSITIONS,
)


CHAIN_BOUNDARIES = 2
COMPLETE_CHAIN_CANDIDATES = CHAIN_BOUNDARIES * BOUNDARY_CONTEXTS
DIRECTIONS = ("n_to_c", "c_to_n")


def _complete_boundary_frontier(sequence: str, direction: str) -> tuple[list, list]:
    domain = closed_angle_domain()
    candidate_states = tuple(sorted(domain.values()))
    frontier = [((0, 1.0, 0.0), tuple())]
    trace = []
    for step in range(len(sequence) - 1):
        expanded = []
        for _, path in frontier:
            for state in candidate_states:
                if direction == "n_to_c":
                    candidate = path + (state,)
                    key = _candidate_key(sequence, list(candidate))
                elif direction == "c_to_n":
                    candidate = (state,) + path
                    start = len(sequence) - 1 - len(candidate)
                    key = _candidate_key(sequence[start:], list(candidate))
                else:
                    raise ValueError(f"unsupported chain direction: {direction}")
                expanded.append((key, candidate))

        active_count = step + 1
        if active_count < BOUNDARY_RESIDUES:
            frontier = sorted(expanded, key=lambda item: (item[0], item[1]))
            expected_contexts = 2 ** active_count
            inbound_counts = [1] * expected_contexts
        else:
            grouped = {}
            for item in expanded:
                context = (
                    item[1][-BOUNDARY_RESIDUES:]
                    if direction == "n_to_c"
                    else item[1][:BOUNDARY_RESIDUES]
                )
                grouped.setdefault(context, []).append(item)
            if len(grouped) != BOUNDARY_CONTEXTS:
                raise RuntimeError(f"V36 {direction} frontier lost a boundary context")
            frontier = []
            inbound_counts = []
            for context in sorted(grouped):
                arrivals = sorted(grouped[context], key=lambda item: (item[0], item[1]))
                expected_inbound = 1 if active_count == BOUNDARY_RESIDUES else 2
                if len(arrivals) != expected_inbound:
                    raise RuntimeError(f"V36 {direction} context has incomplete arrivals")
                frontier.append(arrivals[0])
                inbound_counts.append(len(arrivals))
            frontier.sort(key=lambda item: (item[0], item[1]))
            expected_contexts = BOUNDARY_CONTEXTS
        if len(frontier) != expected_contexts:
            raise RuntimeError(f"V36 {direction} frontier census drifted")
        trace.append({
            "direction": direction,
            "active_states": active_count,
            "expanded_transitions": len(expanded),
            "retained_contexts": len(frontier),
            "inbound_per_context": sorted(set(inbound_counts)),
        })
    return frontier, trace


def select_state_path_v36(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) < BOUNDARY_RESIDUES + 1:
        raise ValueError("V36 complete-chain reconciliation requires at least four residues")
    if COMPLETE_CHAIN_CANDIDATES != QUARTET_TRANSITIONS:
        raise RuntimeError("V36 two-boundary candidate census did not close")

    domain = closed_angle_domain()
    state_modes = {state: mode for mode, state in domain.items()}
    directional_candidates = []
    boundary_trace = []
    for direction in DIRECTIONS:
        frontier, trace = _complete_boundary_frontier(sequence, direction)
        boundary_trace.extend(trace)
        if len(frontier) != BOUNDARY_CONTEXTS:
            raise RuntimeError(f"V36 {direction} did not expose every final context")
        for _, path in frontier:
            context = (
                path[-BOUNDARY_RESIDUES:]
                if direction == "n_to_c"
                else path[:BOUNDARY_RESIDUES]
            )
            directional_candidates.append({
                "direction": direction,
                "context": list(context),
                "key": list(_candidate_key(sequence, list(path))),
                "path": list(path),
            })
    if len(directional_candidates) != COMPLETE_CHAIN_CANDIDATES:
        raise RuntimeError("V36 did not generate the complete chain candidate census")
    by_direction = {
        direction: sum(row["direction"] == direction for row in directional_candidates)
        for direction in DIRECTIONS
    }
    if set(by_direction.values()) != {BOUNDARY_CONTEXTS}:
        raise RuntimeError("V36 candidate coverage differs between chain boundaries")

    ranked = sorted(
        directional_candidates,
        key=lambda row: (tuple(row["key"]), tuple(row["path"])),
    )
    selected = ranked[0]
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
        "chain_boundaries": CHAIN_BOUNDARIES,
        "boundary_contexts": BOUNDARY_CONTEXTS,
        "complete_chain_candidates": COMPLETE_CHAIN_CANDIDATES,
        "candidates_per_boundary": by_direction,
        "boundary_trace": boundary_trace,
        "reconciliation_trace": directional_candidates,
        "selected_direction": selected["direction"],
        "selected_context": selected["context"],
        "final_key": selected["key"],
    }
