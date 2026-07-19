#!/usr/bin/env python3
"""Provenance-isolated sequence-to-24-lattice forward-forcing selector v3.

V3 preserves the registered dimensionless v2 ordering while removing every
runtime import from the legacy all-purpose predictor and v1 selector.  Its only
project dependency is the target-incapable backbone geometry constitution.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
    from tools.residue_partition_v1 import (
        AMINO_ACIDS, HYDROPHOBIC_PACKING, verify_registered_partition)
except ImportError:  # direct execution from tools/
    from protein_backbone_geometry_v1 import build_backbone_coordinates
    from residue_partition_v1 import (
        AMINO_ACIDS, HYDROPHOBIC_PACKING, verify_registered_partition)


LATTICE_DEGREES = tuple(range(-180, 180, 15))
LATTICE_STATES = tuple(
    (math.radians(phi), math.radians(psi))
    for phi in LATTICE_DEGREES
    for psi in LATTICE_DEGREES
)
CANONICAL_STATE = 0
HYDROPHOBICS = HYDROPHOBIC_PACKING
RESIDUE_PARTITION = verify_registered_partition()


def forced_beam_width() -> int:
    """The finite path capacity is the counted 24-state lattice axis."""
    axis = len(LATTICE_DEGREES)
    if axis * axis != len(LATTICE_STATES):
        raise RuntimeError("24-lattice axis/state census did not close")
    return axis


def validate_sequence(sequence: str) -> str:
    sequence = str(sequence).strip().upper()
    if not sequence:
        raise ValueError("sequence must be non-empty")
    unsupported = sorted(set(sequence) - AMINO_ACIDS)
    if unsupported:
        raise ValueError(f"unsupported amino-acid symbols: {''.join(unsupported)}")
    return sequence


def angles_for_state(state: int) -> tuple[float, float]:
    if not isinstance(state, int) or not 0 <= state < len(LATTICE_STATES):
        raise ValueError(f"24-lattice state outside [0,575]: {state!r}")
    return LATTICE_STATES[state]


def active_candidates(index: int, length: int):
    if length < 1 or index < 0 or index >= length - 1:
        return ()
    if index == 0:
        return range(len(LATTICE_DEGREES))
    return range(len(LATTICE_STATES))


def build_lookahead_prefix(sequence: str, state_path: list[int]):
    prefix_length = len(state_path) + 1
    if prefix_length > len(sequence):
        raise ValueError("state path is longer than the active sequence prefix")
    states = list(state_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    return build_backbone_coordinates(sequence[:prefix_length], phi, psi)


def dimensionless_topology_key(sequence: str, ca_coordinates: np.ndarray):
    count = len(ca_coordinates)
    if count < 2:
        return (0, 1.0, 0.0)
    adjacent_d2 = [
        float(np.sum((ca_coordinates[index + 1] - ca_coordinates[index]) ** 2))
        for index in range(count - 1)
    ]
    step_d2 = sum(adjacent_d2) / len(adjacent_d2)
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("selector-v3 produced an invalid endogenous C-alpha step")

    non_neighbour = []
    hydrophobic = []
    for left in range(count):
        for right in range(left + 2, count):
            distance_d2 = float(
                np.sum((ca_coordinates[right] - ca_coordinates[left]) ** 2)
            )
            non_neighbour.append(distance_d2)
            if sequence[left] in HYDROPHOBICS and sequence[right] in HYDROPHOBICS:
                hydrophobic.append(distance_d2)

    violations = sum(distance < step_d2 for distance in non_neighbour)
    background = (
        sum(non_neighbour) / len(non_neighbour) if non_neighbour else step_d2
    )
    hydrophobic_dispersion = (
        (sum(hydrophobic) / len(hydrophobic)) / background
        if hydrophobic else 1.0
    )
    center = np.mean(ca_coordinates, axis=0)
    radius_d2 = float(np.sum((ca_coordinates - center) ** 2)) / count
    key = (violations, hydrophobic_dispersion, radius_d2 / step_d2)
    if not all(math.isfinite(value) for value in key):
        raise RuntimeError("selector-v3 produced a non-finite topology key")
    return key


def _candidate_key(sequence: str, state_path: list[int]):
    atoms = build_lookahead_prefix(sequence, state_path)
    ca = np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float
    )
    return dimensionless_topology_key(sequence[:len(ca)], ca)


def select_state_path_v3(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    beam_width = forced_beam_width()
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_key": [0, 1.0, 0.0], "atoms": atoms,
        }

    beam = [((0, 1.0, 0.0), tuple())]
    score_trace = []
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = list(path) + [state]
                expanded.append((_candidate_key(sequence, candidate), tuple(candidate)))
        expanded.sort(key=lambda item: (item[0], item[1]))
        beam = expanded[:beam_width]
        score_trace.append({
            "active_state": index,
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
