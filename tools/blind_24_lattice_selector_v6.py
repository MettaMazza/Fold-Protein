#!/usr/bin/env python3
"""Selector v6: signed quartet orientation from the forced alpha/beta orbits.

V5 established the four-residue union of two overlapping three-residue planes,
but its distance topology is reflection-invariant.  V6 adds the dimensionless
signed scalar triple product of the three consecutive C-alpha steps.  The two
reference signatures are generated at runtime from the already engine-checked
alpha and beta angle fractions through the registered peptide-geometry
constitution.  They are not read from a target and are not fitted constants.

Candidates are ordered lexicographically by distance to the nearer generated
alpha/beta orientation signature, terminal-quartet v5 topology, and complete-
prefix v3 topology.  There is no weighted blend, cutoff, tolerance, target, or
caller-selected beam width.
"""
from __future__ import annotations

from fractions import Fraction
import math

import numpy as np

try:
    from tools.blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, LATTICE_DEGREES, active_candidates, angles_for_state,
        forced_beam_width, validate_sequence)
    from tools.blind_24_lattice_selector_v5 import (
        ORIENTATION_CONSTITUTION, ORIENTATION_QUARTET, QUARTET_OVERLAP,
        complete_prefix_key, interwindow_orientation_key, locally_eligible)
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
except ImportError:  # direct execution from tools/
    from blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, LATTICE_DEGREES, active_candidates, angles_for_state,
        forced_beam_width, validate_sequence)
    from blind_24_lattice_selector_v5 import (
        ORIENTATION_CONSTITUTION, ORIENTATION_QUARTET, QUARTET_OVERLAP,
        complete_prefix_key, interwindow_orientation_key, locally_eligible)
    from protein_backbone_geometry_v1 import build_backbone_coordinates


CIRCLE_DEGREES = Fraction(360, 1)
ALPHA_ANGLES_DEGREES = (
    -CIRCLE_DEGREES / 6,
    -CIRCLE_DEGREES / 8,
)
BETA_ANGLES_DEGREES = (
    -CIRCLE_DEGREES / 3,
    3 * CIRCLE_DEGREES / 8,
)


def _ca(atoms) -> np.ndarray:
    return np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)


def normalized_signed_quartet_volume(ca_coordinates: np.ndarray) -> float:
    """Return signed volume divided by the three generated step lengths."""
    coordinates = np.asarray(ca_coordinates, dtype=float)
    if coordinates.shape != (ORIENTATION_QUARTET, 3):
        raise ValueError("signed orientation requires exactly four C-alpha points")
    steps = np.diff(coordinates, axis=0)
    denominator = float(np.prod(np.linalg.norm(steps, axis=1)))
    if not math.isfinite(denominator) or denominator <= 0:
        raise RuntimeError("degenerate generated quartet orientation")
    signed = float(np.dot(np.cross(steps[0], steps[1]), steps[2]))
    result = signed / denominator
    if not math.isfinite(result):
        raise RuntimeError("non-finite generated quartet orientation")
    return result


def _generated_orbit_signature(angle_pair: tuple[Fraction, Fraction]) -> float:
    phi = math.radians(float(angle_pair[0]))
    psi = math.radians(float(angle_pair[1]))
    states = [(phi, psi)] * QUARTET_OVERLAP + [
        angles_for_state(CANONICAL_STATE)]
    atoms = build_backbone_coordinates(
        "A" * ORIENTATION_QUARTET,
        [state[0] for state in states],
        [state[1] for state in states],
    )
    return normalized_signed_quartet_volume(_ca(atoms))


GENERATED_ORBIT_SIGNATURES = {
    "alpha": _generated_orbit_signature(ALPHA_ANGLES_DEGREES),
    "beta": _generated_orbit_signature(BETA_ANGLES_DEGREES),
}


def verify_generated_orientation_modes() -> dict:
    """Halt unless the forced angle modes generate distinct signed quartets."""
    alpha = GENERATED_ORBIT_SIGNATURES["alpha"]
    beta = GENERATED_ORBIT_SIGNATURES["beta"]
    if not alpha > 0:
        raise RuntimeError("forced alpha orbit did not generate positive orientation")
    if not beta < 0:
        raise RuntimeError("forced beta orbit did not generate negative orientation")
    if alpha == beta:
        raise RuntimeError("forced orientation modes did not separate")
    return {
        "alpha": alpha,
        "beta": beta,
        "source_angles_degrees": {
            "alpha": [str(value) for value in ALPHA_ANGLES_DEGREES],
            "beta": [str(value) for value in BETA_ANGLES_DEGREES],
        },
    }


ORIENTATION_MODES = verify_generated_orientation_modes()


def _circular_lattice_distance(left: int, right: int) -> int:
    difference = abs(left - right)
    return min(difference, len(LATTICE_DEGREES) - difference)


def precursor_orbit_key(state_path: list[int]):
    """Keep exact alpha/beta preimages before four points are observable."""
    if not state_path:
        return (0,)
    mode_indices = {}
    for name, angles in (
            ("alpha", ALPHA_ANGLES_DEGREES),
            ("beta", BETA_ANGLES_DEGREES)):
        phi_index = LATTICE_DEGREES.index(int(angles[0]))
        psi_index = LATTICE_DEGREES.index(int(angles[1]))
        mode_indices[name] = (phi_index, psi_index)

    distances = []
    for phi_mode, psi_mode in mode_indices.values():
        total = _circular_lattice_distance(state_path[0] % 24, psi_mode)
        for state in state_path[1:]:
            phi_index, psi_index = divmod(state, 24)
            total += _circular_lattice_distance(phi_index, phi_mode)
            total += _circular_lattice_distance(psi_index, psi_mode)
        distances.append(total)
    return (min(distances),)


def interwindow_signed_orientation(sequence: str, state_path: list[int]):
    """Generate the terminal quartet's signed orientation without a target."""
    prefix_length = len(state_path) + 1
    if prefix_length > len(sequence):
        raise ValueError("state path is longer than the active sequence prefix")
    if prefix_length < ORIENTATION_QUARTET:
        return None
    quartet_sequence = sequence[
        prefix_length - ORIENTATION_QUARTET:prefix_length]
    quartet_states = list(state_path[-QUARTET_OVERLAP:]) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in quartet_states]
    psi = [angles_for_state(state)[1] for state in quartet_states]
    atoms = build_backbone_coordinates(quartet_sequence, phi, psi)
    return normalized_signed_quartet_volume(_ca(atoms))


def orientation_orbit_key(sequence: str, state_path: list[int]):
    """Return distance to the nearer generated alpha/beta signed mode."""
    orientation = interwindow_signed_orientation(sequence, state_path)
    if orientation is None:
        return precursor_orbit_key(state_path)
    distance = min(
        abs(orientation - signature)
        for signature in GENERATED_ORBIT_SIGNATURES.values()
    )
    return (distance,)


def local_orientation_key(sequence: str, state_path: list[int]):
    """Order signed orbit proximity before the v5 quartet topology."""
    return (
        tuple(orientation_orbit_key(sequence, state_path))
        + tuple(interwindow_orientation_key(sequence, state_path))
    )


def selected_orientation_trace(sequence: str, states: list[int]) -> list[dict]:
    """Expose every selected target-free quartet orientation and nearer mode."""
    trace = []
    for end in range(ORIENTATION_QUARTET, len(sequence) + 1):
        active_path = states[:end - 1]
        signed = interwindow_signed_orientation(sequence[:end], active_path)
        distances = {
            name: abs(signed - signature)
            for name, signature in GENERATED_ORBIT_SIGNATURES.items()
        }
        nearest = min(distances, key=lambda name: (distances[name], name))
        trace.append({
            "residue_positions_one_based": [
                end - ORIENTATION_QUARTET + 1, end],
            "sequence": sequence[end - ORIENTATION_QUARTET:end],
            "normalized_signed_volume": signed,
            "nearest_generated_mode": nearest,
            "mode_distance": distances[nearest],
        })
    return trace


def select_state_path_v6(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    beam_width = forced_beam_width()
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_key": [0.0, 0, 1.0, 0.0, 0, 1.0, 0.0],
            "orientation_modes": ORIENTATION_MODES,
            "orientation_trace": [], "atoms": atoms,
        }

    beam = [((0.0, 0, 1.0, 0.0, 0, 1.0, 0.0), tuple())]
    score_trace = []
    for index in range(len(sequence) - 1):
        local_candidates = []
        for _, path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                local = local_orientation_key(sequence, list(candidate))
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
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "atoms": atoms,
    }
