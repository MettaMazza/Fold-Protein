#!/usr/bin/env python3
"""Selector v7: binary-balanced preservation of alpha and beta modes.

V6 generated the two signed orientation modes directly from the forced alpha
and beta angles, but a single undivided 24-state frontier selected alpha at
every quartet.  V7 uses the theorem-derived binary count to divide the counted
24-state lattice-axis capacity into two exact 12-path mode frontiers.  Neither
generated mode can be erased before the complete sequence topology compares
them.

Within each mode, signed-orbit distance and quartet topology retain the best
12 paths.  Across the two preserved mode frontiers, complete-prefix topology
selects the continuation, followed by the local relation and state tuple.  No
target, fitted weight, reward, tolerance, or caller-selected capacity enters.
"""
from __future__ import annotations

try:
    from tools.blind_24_lattice_selector_v3 import (
        LATTICE_DEGREES, active_candidates, forced_beam_width,
        validate_sequence)
    from tools.blind_24_lattice_selector_v5 import (
        ORIENTATION_CONSTITUTION, complete_prefix_key, locally_eligible)
    from tools.blind_24_lattice_selector_v6 import (
        ALPHA_ANGLES_DEGREES, BETA_ANGLES_DEGREES,
        GENERATED_ORBIT_SIGNATURES, ORIENTATION_MODES,
        interwindow_signed_orientation, local_orientation_key,
        select_state_path_v6, selected_orientation_trace)
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
    from tools.blind_24_lattice_selector_v3 import angles_for_state
except ImportError:  # direct execution from tools/
    from blind_24_lattice_selector_v3 import (
        LATTICE_DEGREES, active_candidates, forced_beam_width,
        validate_sequence)
    from blind_24_lattice_selector_v5 import (
        ORIENTATION_CONSTITUTION, complete_prefix_key, locally_eligible)
    from blind_24_lattice_selector_v6 import (
        ALPHA_ANGLES_DEGREES, BETA_ANGLES_DEGREES,
        GENERATED_ORBIT_SIGNATURES, ORIENTATION_MODES,
        interwindow_signed_orientation, local_orientation_key,
        select_state_path_v6, selected_orientation_trace)
    from protein_backbone_geometry_v1 import build_backbone_coordinates
    from blind_24_lattice_selector_v3 import angles_for_state


BINARY_MODE_COUNT = 2
MODE_NAMES = ("alpha", "beta")


def forced_mode_capacity() -> int:
    """Divide the counted 24-axis frontier by the fold-derived binary count."""
    width = forced_beam_width()
    if len(MODE_NAMES) != BINARY_MODE_COUNT:
        raise RuntimeError("generated orientation modes do not close as binary")
    if width % BINARY_MODE_COUNT:
        raise RuntimeError("24-state frontier does not divide by binary count")
    capacity = width // BINARY_MODE_COUNT
    if capacity * BINARY_MODE_COUNT != width:
        raise RuntimeError("binary mode capacities do not reconstruct frontier")
    return capacity


MODE_CAPACITY = forced_mode_capacity()


def _circular_distance(left: int, right: int) -> int:
    difference = abs(left - right)
    return min(difference, len(LATTICE_DEGREES) - difference)


def precursor_mode_distances(state_path: list[int]) -> dict[str, int]:
    """Return exact 24-lattice distances to consistent alpha/beta preimages."""
    distances = {}
    for name, angles in (
            ("alpha", ALPHA_ANGLES_DEGREES),
            ("beta", BETA_ANGLES_DEGREES)):
        phi_mode = LATTICE_DEGREES.index(int(angles[0]))
        psi_mode = LATTICE_DEGREES.index(int(angles[1]))
        total = _circular_distance(state_path[0] % 24, psi_mode)
        for state in state_path[1:]:
            phi_index, psi_index = divmod(state, 24)
            total += _circular_distance(phi_index, phi_mode)
            total += _circular_distance(psi_index, psi_mode)
        distances[name] = total
    return distances


def candidate_mode(sequence: str, state_path: list[int]) -> str:
    """Classify a candidate by its nearer generated mode, target-free."""
    signed = interwindow_signed_orientation(sequence, state_path)
    if signed is None:
        distances = precursor_mode_distances(state_path)
    else:
        distances = {
            name: abs(signed - signature)
            for name, signature in GENERATED_ORBIT_SIGNATURES.items()
        }
    minimum = min(distances.values())
    tied = [name for name in MODE_NAMES if distances[name] == minimum]
    if len(tied) == 1:
        return tied[0]
    # The two exact circular bisectors are assigned to opposite binary halves
    # of the 24-state psi axis, preserving a 12/12 initial census.
    psi_half = (state_path[-1] % len(LATTICE_DEGREES)) // MODE_CAPACITY
    return MODE_NAMES[psi_half]


def select_state_path_v7(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) == 1:
        baseline = select_state_path_v6(sequence)
        baseline["mode_capacity"] = MODE_CAPACITY
        baseline["mode_balance_trace"] = []
        return baseline

    beam = [tuple()]
    score_trace = []
    for index in range(len(sequence) - 1):
        by_mode = {name: [] for name in MODE_NAMES}
        for path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                local = local_orientation_key(sequence, list(candidate))
                mode = candidate_mode(sequence, list(candidate))
                by_mode[mode].append((local, candidate))

        retained = []
        mode_row = {}
        for mode in MODE_NAMES:
            eligible = locally_eligible(by_mode[mode], MODE_CAPACITY)
            expanded = []
            for local, candidate in eligible:
                complete = complete_prefix_key(sequence, list(candidate))
                within_mode_key = tuple(local) + tuple(complete)
                cross_mode_key = tuple(complete) + tuple(local)
                expanded.append((within_mode_key, cross_mode_key, candidate))
            expanded.sort(key=lambda item: (item[0], item[2]))
            held = expanded[:MODE_CAPACITY]
            retained.extend((cross, candidate) for _, cross, candidate in held)
            mode_row[mode] = {
                "expanded": len(by_mode[mode]),
                "locally_eligible": len(eligible),
                "retained": len(held),
            }
        retained.sort(key=lambda item: (item[0], item[1]))
        beam = [candidate for _, candidate in retained]
        score_trace.append({
            "active_state": index,
            "mode_capacity": MODE_CAPACITY,
            "modes": mode_row,
            "retained": len(beam),
            "best_cross_mode_key": list(retained[0][0]),
            "worst_cross_mode_key": list(retained[-1][0]),
        })

    final_candidates = []
    for path in beam:
        local = local_orientation_key(sequence, list(path))
        complete = complete_prefix_key(sequence, list(path))
        cross_mode_key = tuple(complete) + tuple(local)
        final_candidates.append((cross_mode_key, path))
    final_candidates.sort(key=lambda item: (item[0], item[1]))
    final_key, active_path = final_candidates[0]
    states = list(active_path) + [0]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "score_trace": score_trace,
        "final_key": list(final_key),
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "mode_capacity": MODE_CAPACITY,
        "mode_balance_trace": [row["modes"] for row in score_trace],
        "atoms": atoms,
    }
