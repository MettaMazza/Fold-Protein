#!/usr/bin/env python3
"""Selector v5: four-residue orientation of overlapping colour windows.

Three C-alpha coordinates define one local plane.  Consecutive three-residue
colour windows share the binary count of two residues; their union therefore
has c + c - b = 4 residues and is the first local object that contains their
relative orientation.  V5 orders candidates first by the generated topology
of that terminal quartet and then by the complete-prefix v3 relation.

No target, fitted weight, tolerance, or numerical blend enters the ordering.
The local frontier calculation is exact for the lexicographic relation: every
candidate at or below the width-th local key, including all boundary ties, is
passed to the complete-prefix secondary ordering.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np

try:
    from tools.blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, active_candidates, angles_for_state,
        build_lookahead_prefix, dimensionless_topology_key, forced_beam_width,
        validate_sequence)
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
except ImportError:  # direct execution from tools/
    from blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, active_candidates, angles_for_state,
        build_lookahead_prefix, dimensionless_topology_key, forced_beam_width,
        validate_sequence)
    from protein_backbone_geometry_v1 import build_backbone_coordinates


BINARY_PLANE_OVERLAP = 2
COLOUR_PLANE_WINDOW = 3
ORIENTATION_QUARTET = (
    COLOUR_PLANE_WINDOW + COLOUR_PLANE_WINDOW - BINARY_PLANE_OVERLAP)
QUARTET_OVERLAP = COLOUR_PLANE_WINDOW


def verify_orientation_constitution() -> dict:
    """Close the quartet, its colour-window overlap, and its One advance."""
    if ORIENTATION_QUARTET != 4:
        raise RuntimeError("two colour windows did not close as a quartet")
    if QUARTET_OVERLAP != 3:
        raise RuntimeError("orientation quartets do not share a colour window")
    if ORIENTATION_QUARTET - QUARTET_OVERLAP != 1:
        raise RuntimeError("orientation quartet does not advance by the One")
    return {
        "orientation_residues": ORIENTATION_QUARTET,
        "overlap_residues": QUARTET_OVERLAP,
        "new_residues_per_step": ORIENTATION_QUARTET - QUARTET_OVERLAP,
    }


ORIENTATION_CONSTITUTION = verify_orientation_constitution()


def _ca(atoms) -> np.ndarray:
    return np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)


def interwindow_orientation_key(sequence: str, state_path: list[int]):
    """Return the target-free terminal four-residue topology key."""
    prefix_length = len(state_path) + 1
    if prefix_length > len(sequence):
        raise ValueError("state path is longer than the active sequence prefix")
    if prefix_length < ORIENTATION_QUARTET:
        return (0, 1.0, 0.0)

    quartet_sequence = sequence[
        prefix_length - ORIENTATION_QUARTET:prefix_length]
    quartet_states = list(state_path[-QUARTET_OVERLAP:]) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in quartet_states]
    psi = [angles_for_state(state)[1] for state in quartet_states]
    atoms = build_backbone_coordinates(quartet_sequence, phi, psi)
    return dimensionless_topology_key(quartet_sequence, _ca(atoms))


def complete_prefix_key(sequence: str, state_path: list[int]):
    """Return the complete-prefix v3 topology key as secondary relation."""
    atoms = build_lookahead_prefix(sequence, state_path)
    coordinates = _ca(atoms)
    return dimensionless_topology_key(sequence[:len(coordinates)], coordinates)


def locally_eligible(
        candidates: Iterable[tuple[tuple, tuple[int, ...]]], width: int):
    """Keep every candidate at or below the exact width-th local boundary."""
    ordered = sorted(candidates, key=lambda item: (item[0], item[1]))
    if len(ordered) <= width:
        return ordered
    boundary = ordered[width - 1][0]
    return [item for item in ordered if item[0] <= boundary]


def select_state_path_v5(sequence: str) -> dict:
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
                local = interwindow_orientation_key(sequence, list(candidate))
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
