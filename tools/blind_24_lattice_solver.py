#!/usr/bin/env python3
"""Sequence-only 24-lattice selector.

The lattice is fixed and parameter-free.  The present compaction score and beam
capacity are explicitly registered for the sequence forward-forcing execution.
No native structure or target-derived quantity enters this module.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np

try:
    from tools.predict_structure import build_backbone_coordinates
except ImportError:  # direct execution from tools/
    from predict_structure import build_backbone_coordinates


LATTICE_DEGREES = tuple(range(-180, 180, 15))
SFT_CANDIDATES = tuple(
    (math.radians(phi), math.radians(psi))
    for phi in LATTICE_DEGREES
    for psi in LATTICE_DEGREES
)
CANONICAL_STATE = 0
HYDROPHOBICS = frozenset("VILMFWCY")
AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")


@dataclass(frozen=True)
class SelectorConfig:
    beam_width: int = 24                 # registered finite capacity
    nonlocal_separation: int = 3         # registered score relation
    contact_cutoff: float = 8.0          # Å
    contact_reward: float = 10.0
    clash_cutoff: float = 3.2            # Å


def validate_sequence(sequence: str) -> str:
    sequence = str(sequence).strip().upper()
    if not sequence:
        raise ValueError("sequence must be non-empty")
    invalid = sorted(set(sequence) - AMINO_ACIDS)
    if invalid:
        raise ValueError(f"unsupported amino-acid symbols: {''.join(invalid)}")
    return sequence


def angles_for_state(state: int) -> tuple[float, float]:
    if not isinstance(state, int) or not 0 <= state < len(SFT_CANDIDATES):
        raise ValueError(f"24-lattice state outside [0,575]: {state!r}")
    return SFT_CANDIDATES[state]


def active_candidates(index: int, length: int) -> Iterable[int]:
    """States whose geometry can affect a scored Cα at this depth.

    The first residue's phi is unused, so it is fixed to -180° and only its 24
    psi states are searched.  The last residue has no Cα-active dihedral and is
    appended canonically after selection.
    """
    if length < 1 or index < 0 or index >= length - 1:
        return ()
    if index == 0:
        return range(24)
    return range(len(SFT_CANDIDATES))


def build_lookahead_prefix(sequence: str, state_path: list[int]):
    """Build one residue beyond the newest state so that it is causally visible."""
    prefix_length = len(state_path) + 1
    if prefix_length > len(sequence):
        raise ValueError("state path is longer than the active sequence prefix")
    states = list(state_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    prefix = sequence[:prefix_length]
    return build_backbone_coordinates(prefix, ["C"] * prefix_length, phi, psi)


def score_geometric_topology(sequence: str, ca_coordinates: np.ndarray,
                             config: SelectorConfig) -> float:
    """Registered sequence-and-geometry score retained for selector v1."""
    count = len(ca_coordinates)
    if count < 2:
        return 0.0
    center = np.mean(ca_coordinates, axis=0)
    radius = math.sqrt(float(np.sum((ca_coordinates - center) ** 2)) / count)
    reward = 0.0
    hydrophobic = [i for i, residue in enumerate(sequence) if residue in HYDROPHOBICS]
    for left_pos, left in enumerate(hydrophobic):
        for right in hydrophobic[left_pos + 1:]:
            if right - left <= config.nonlocal_separation:
                continue
            distance = float(np.linalg.norm(ca_coordinates[left] - ca_coordinates[right]))
            if distance < config.contact_cutoff:
                reward += config.contact_reward / distance
    return radius - reward


def _candidate_score(sequence: str, state_path: list[int], config: SelectorConfig):
    atoms = build_lookahead_prefix(sequence, state_path)
    ca = np.asarray([atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)
    if len(ca) >= 4:
        new_ca = ca[-1]
        if np.any(np.linalg.norm(ca[:-3] - new_ca, axis=1) < config.clash_cutoff):
            return None
    score = score_geometric_topology(sequence[:len(ca)], ca, config)
    if not math.isfinite(score):
        raise RuntimeError("selector produced a non-finite score")
    return score


def select_state_path(sequence: str, config: SelectorConfig | None = None) -> dict:
    """Select a deterministic target-isolated state path and return its evidence."""
    sequence = validate_sequence(sequence)
    config = config or SelectorConfig()
    if not isinstance(config.beam_width, int) or config.beam_width < 1:
        raise ValueError("beam width must be a positive integer")
    if len(sequence) == 1:
        states = [CANONICAL_STATE]
        phi = [angles_for_state(0)[0]]
        psi = [angles_for_state(0)[1]]
        atoms = build_backbone_coordinates(sequence, ["C"], phi, psi)
        return {"states": states, "score_trace": [], "final_score": 0.0, "atoms": atoms}

    beam = [(0.0, tuple())]
    score_trace = []
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = list(path) + [state]
                score = _candidate_score(sequence, candidate, config)
                if score is not None:
                    expanded.append((score, tuple(candidate)))
        if not expanded:
            raise RuntimeError(f"beam exhausted at active state {index}")
        expanded.sort(key=lambda item: (item[0], item[1]))
        beam = expanded[:config.beam_width]
        score_trace.append(
            {"active_state": index, "retained": len(beam),
             "best": beam[0][0], "worst": beam[-1][0]}
        )

    final_score, active_path = beam[0]
    states = list(active_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, ["C"] * len(sequence), phi, psi)
    return {
        "states": states,
        "score_trace": score_trace,
        "final_score": final_score,
        "atoms": atoms,
    }
