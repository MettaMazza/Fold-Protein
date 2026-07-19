#!/usr/bin/env python3
"""Selector v4: binary-overlap propagation of colour-window geometry.

The SFT colour generator supplies a three-residue local construction window.
Adjacent colour windows share the binary count of two residues.  V4 therefore
orders every candidate first by the generated geometry of its terminal
three-residue window, then by the complete-prefix topology relation inherited
from v3.  No target, fitted weight, tolerance, or numerical blend enters the
ordering.

The two-stage frontier calculation is exact for that lexicographic order: a
candidate whose local key is greater than the 24th local key cannot enter the
24-state retained frontier under any complete-prefix secondary key.  Only the
eligible local frontier and every candidate tied at its boundary require the
more expensive complete-prefix construction.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np

try:
    from tools.blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, LATTICE_DEGREES, LATTICE_STATES, active_candidates,
        angles_for_state, build_lookahead_prefix, dimensionless_topology_key,
        forced_beam_width, validate_sequence)
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
except ImportError:  # direct execution from tools/
    from blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, LATTICE_DEGREES, LATTICE_STATES, active_candidates,
        angles_for_state, build_lookahead_prefix, dimensionless_topology_key,
        forced_beam_width, validate_sequence)
    from protein_backbone_geometry_v1 import build_backbone_coordinates


BINARY_OVERLAP = 2
COLOUR_WINDOW = 3


def verify_overlap_constitution() -> dict:
    """Prove the local propagation window closes as c with b shared parts."""
    if COLOUR_WINDOW - 1 != BINARY_OVERLAP:
        raise RuntimeError("colour window does not advance through binary overlap")
    return {
        "window_residues": COLOUR_WINDOW,
        "overlap_residues": BINARY_OVERLAP,
        "new_residues_per_step": COLOUR_WINDOW - BINARY_OVERLAP,
    }


OVERLAP_CONSTITUTION = verify_overlap_constitution()


def _ca(atoms) -> np.ndarray:
    return np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)


def overlap_orientation_key(sequence: str, state_path: list[int]):
    """Return the target-free terminal c-window key for an active state path."""
    prefix_length = len(state_path) + 1
    if prefix_length > len(sequence):
        raise ValueError("state path is longer than the active sequence prefix")
    if prefix_length < COLOUR_WINDOW:
        return (0, 1.0, 0.0)

    window_sequence = sequence[
        prefix_length - COLOUR_WINDOW:prefix_length]
    window_states = list(state_path[-BINARY_OVERLAP:]) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in window_states]
    psi = [angles_for_state(state)[1] for state in window_states]
    atoms = build_backbone_coordinates(window_sequence, phi, psi)
    return dimensionless_topology_key(window_sequence, _ca(atoms))


def complete_prefix_key(sequence: str, state_path: list[int]):
    """Return the complete-prefix v3 topology key as the secondary relation."""
    atoms = build_lookahead_prefix(sequence, state_path)
    coordinates = _ca(atoms)
    return dimensionless_topology_key(sequence[:len(coordinates)], coordinates)


def locally_eligible(
        candidates: Iterable[tuple[tuple, tuple[int, ...]]], width: int):
    """Keep every candidate at or below the exact width-th local-key boundary."""
    ordered = sorted(candidates, key=lambda item: (item[0], item[1]))
    if len(ordered) <= width:
        return ordered
    boundary = ordered[width - 1][0]
    return [item for item in ordered if item[0] <= boundary]


def select_state_path_v4(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    beam_width = forced_beam_width()
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_key": [0, 1.0, 0.0, 0, 1.0, 0.0], "atoms": atoms,
        }

    beam = [((0, 1.0, 0.0, 0, 1.0, 0.0), tuple())]
    score_trace = []
    for index in range(len(sequence) - 1):
        local_candidates = []
        for _, path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                local = overlap_orientation_key(sequence, list(candidate))
                local_candidates.append((local, candidate))

        eligible = locally_eligible(local_candidates, beam_width)
        expanded = []
        for local, candidate in eligible:
            complete = complete_prefix_key(sequence, list(candidate))
            expanded.append((tuple(local) + tuple(complete), candidate))
        expanded.sort(key=lambda item: (item[0], item[1]))
        beam = expanded[:beam_width]
        score_trace.append({
            "active_state": index,
            "expanded": len(local_candidates),
            "locally_eligible": len(eligible),
            "retained": len(beam),
            "best_key": list(beam[0][0]),
            "worst_key": list(beam[-1][0]),
        })

    final_key, active_path = beam[0]
    states = list(active_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "score_trace": score_trace,
        "final_key": list(final_key),
        "atoms": atoms,
    }
