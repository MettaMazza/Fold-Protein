#!/usr/bin/env python3
"""External-length-cutoff-free target-isolated selector-v2 experiment.

This is the registered sequence forward-forcing selector. It removes selector-v1's
Å cutoffs and reward scale and orders generated geometry dimensionlessly.
The only retained capacity is the finite beam.  Candidate ordering uses ratios to
the chain's own mean adjacent Cα step, so it has no external length scale.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

try:
    from tools.blind_24_lattice_solver import (
        CANONICAL_STATE,
        SFT_CANDIDATES,
        active_candidates,
        angles_for_state,
        build_lookahead_prefix,
        validate_sequence,
    )
    from tools.predict_structure import build_backbone_coordinates
except ImportError:  # direct execution from tools/
    from blind_24_lattice_solver import (
        CANONICAL_STATE,
        SFT_CANDIDATES,
        active_candidates,
        angles_for_state,
        build_lookahead_prefix,
        validate_sequence,
    )
    from predict_structure import build_backbone_coordinates


HYDROPHOBICS = frozenset("VILMFWCY")


@dataclass(frozen=True)
class SelectorV2Config:
    beam_width: int = 24  # registered finite path capacity


def dimensionless_topology_key(sequence: str, ca_coordinates: np.ndarray):
    """Return a target-free lexicographic ordering key.

    1. Self-exclusion tests a One-normalised candidate boundary: a non-neighbour
       Cα pair may not be closer than the chain's own mean adjacent Cα step.
    2. Hydrophobic dispersion is the mean hydrophobic-pair squared distance
       divided by the mean non-neighbour squared distance.
    3. Global compaction is radius-of-gyration squared divided by the same
       endogenous adjacent-step scale.

    Hydrophobic classification and lexicographic ordering are explicit inputs to
    the executable route; the engine determines forcing and halts on violation.
    """
    count = len(ca_coordinates)
    if count < 2:
        return (0, 1.0, 0.0)
    adjacent_d2 = [
        float(np.sum((ca_coordinates[i + 1] - ca_coordinates[i]) ** 2))
        for i in range(count - 1)
    ]
    step_d2 = sum(adjacent_d2) / len(adjacent_d2)
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("selector-v2 produced an invalid endogenous C-alpha step")

    nonneighbor = []
    hydro = []
    for left in range(count):
        for right in range(left + 2, count):
            d2 = float(np.sum((ca_coordinates[right] - ca_coordinates[left]) ** 2))
            nonneighbor.append(d2)
            if sequence[left] in HYDROPHOBICS and sequence[right] in HYDROPHOBICS:
                hydro.append(d2)

    violations = sum(1 for d2 in nonneighbor if d2 < step_d2)
    background = sum(nonneighbor) / len(nonneighbor) if nonneighbor else step_d2
    hydro_dispersion = ((sum(hydro) / len(hydro)) / background) if hydro else 1.0
    center = np.mean(ca_coordinates, axis=0)
    radius_d2 = float(np.sum((ca_coordinates - center) ** 2)) / count
    compaction = radius_d2 / step_d2
    key = (violations, hydro_dispersion, compaction)
    if not all(math.isfinite(value) for value in key):
        raise RuntimeError("selector-v2 produced a non-finite topology key")
    return key


def _candidate_key(sequence: str, state_path: list[int]):
    atoms = build_lookahead_prefix(sequence, state_path)
    ca = np.asarray([atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)
    return dimensionless_topology_key(sequence[:len(ca)], ca)


def select_state_path_v2(sequence: str, config: SelectorV2Config | None = None) -> dict:
    """Select a deterministic path using only sequence and generated geometry."""
    sequence = validate_sequence(sequence)
    config = config or SelectorV2Config()
    if not isinstance(config.beam_width, int) or config.beam_width < 1:
        raise ValueError("beam width must be a positive integer")
    if len(sequence) == 1:
        phi = [angles_for_state(CANONICAL_STATE)[0]]
        psi = [angles_for_state(CANONICAL_STATE)[1]]
        atoms = build_backbone_coordinates(sequence, ["C"], phi, psi)
        return {"states": [CANONICAL_STATE], "score_trace": [],
                "final_key": [0, 1.0, 0.0], "atoms": atoms}

    beam = [((0, 1.0, 0.0), tuple())]
    score_trace = []
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = list(path) + [state]
                expanded.append((_candidate_key(sequence, candidate), tuple(candidate)))
        expanded.sort(key=lambda item: (item[0], item[1]))
        beam = expanded[:config.beam_width]
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
    atoms = build_backbone_coordinates(sequence, ["C"] * len(sequence), phi, psi)
    return {"states": states, "score_trace": score_trace,
            "final_key": list(final_key), "atoms": atoms}
