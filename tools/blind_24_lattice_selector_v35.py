#!/usr/bin/env python3
"""V35: complete propagation over the engine-closed Protein boundary graph.

The binary V2 domain gives eight complete three-residue contexts and sixteen
four-residue transitions.  V35 enumerates every transition, advances by one
residue, groups by the exact three-residue overlap, and retains exactly one
representative per context under the already-admitted V3 order and tie break.
No beam width, new score, fitted quantity, or target input exists.
"""
from __future__ import annotations

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    _candidate_key,
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)
from tools.blind_24_lattice_selector_v34 import (
    BINARY_COUNT,
    COLOUR_COUNT,
    _whole_power,
    closed_angle_domain,
)


BOUNDARY_RESIDUES = COLOUR_COUNT
QUARTET_RESIDUES = BINARY_COUNT * BINARY_COUNT
BOUNDARY_CONTEXTS = _whole_power(BINARY_COUNT, BOUNDARY_RESIDUES)
QUARTET_TRANSITIONS = _whole_power(BINARY_COUNT, QUARTET_RESIDUES)


def _context(path: tuple[int, ...]) -> tuple[int, ...]:
    return path[-BOUNDARY_RESIDUES:]


def select_state_path_v35(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    domain = closed_angle_domain()
    candidate_states = tuple(sorted(domain.values()))
    state_modes = {state: mode for mode, state in domain.items()}
    if (len(candidate_states) != BINARY_COUNT
            or BOUNDARY_CONTEXTS != 8 or QUARTET_TRANSITIONS != 16):
        raise RuntimeError("V35 counted boundary graph did not close")
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "modes": ["inactive"],
            "boundary_trace": [], "final_key": [0, 1.0, 0.0],
            "atoms": atoms, "closed_domain": domain,
        }

    frontier = [((0, 1.0, 0.0), tuple())]
    boundary_trace = []
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in frontier:
            for state in candidate_states:
                candidate = tuple(path) + (state,)
                expanded.append((_candidate_key(sequence, list(candidate)), candidate))
        expected_expanded = len(frontier) * BINARY_COUNT
        if len(expanded) != expected_expanded:
            raise RuntimeError("V35 did not enumerate every next-mode transition")

        if index + 1 < BOUNDARY_RESIDUES:
            expanded.sort(key=lambda item: (item[0], item[1]))
            frontier = expanded
            expected_contexts = _whole_power(BINARY_COUNT, index + 1)
            inbound_counts = [1] * expected_contexts
        else:
            grouped: dict[tuple[int, ...], list[tuple[tuple, tuple[int, ...]]]] = {}
            for item in expanded:
                grouped.setdefault(_context(item[1]), []).append(item)
            expected_contexts = BOUNDARY_CONTEXTS
            if len(grouped) != expected_contexts:
                raise RuntimeError("V35 did not preserve every boundary context")
            inbound_counts = []
            frontier = []
            for context in sorted(grouped):
                arrivals = sorted(grouped[context], key=lambda item: (item[0], item[1]))
                expected_inbound = 1 if index + 1 == BOUNDARY_RESIDUES else BINARY_COUNT
                if len(arrivals) != expected_inbound:
                    raise RuntimeError("V35 boundary context has incomplete predecessor modes")
                inbound_counts.append(len(arrivals))
                frontier.append(arrivals[0])
            frontier.sort(key=lambda item: (item[0], item[1]))

        if len(frontier) != expected_contexts:
            raise RuntimeError("V35 frontier differs from the forced context census")
        boundary_trace.append({
            "active_state": index,
            "candidate_domain": list(candidate_states),
            "expanded_transitions": len(expanded),
            "retained_contexts": len(frontier),
            "inbound_per_context": sorted(set(inbound_counts)),
            "best_key": list(frontier[0][0]),
            "worst_key": list(frontier[-1][0]),
        })

    final_key, active_path = min(frontier, key=lambda item: (item[0], item[1]))
    states = list(active_path) + [CANONICAL_STATE]
    modes = [state_modes[state] for state in active_path] + ["inactive"]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "modes": modes,
        "boundary_trace": boundary_trace,
        "final_key": list(final_key),
        "atoms": atoms,
        "closed_domain": domain,
        "boundary_contexts": BOUNDARY_CONTEXTS,
        "quartet_transitions": QUARTET_TRANSITIONS,
    }
