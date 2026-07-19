#!/usr/bin/env python3
"""Selector v8: binary-balanced modes with exact residue charge relation.

V7 preserves both generated alpha and beta orientation branches.  V8 adds the
registered formal side-chain charge signs to the generated sequence topology,
so charged residues can distinguish the preserved geometries by a dimensionless
inverse-distance relation.  Hard self-exclusion remains first; signed charge is
then ordered before hydrophobic dispersion and radius.  No dielectric, cutoff,
weight, target, or empirical mode label is used.
"""
from __future__ import annotations

import numpy as np

try:
    from tools.blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, active_candidates, angles_for_state,
        build_lookahead_prefix, dimensionless_topology_key, validate_sequence)
    from tools.blind_24_lattice_selector_v5 import locally_eligible
    from tools.blind_24_lattice_selector_v6 import (
        ORIENTATION_MODES, interwindow_signed_orientation,
        orientation_orbit_key, selected_orientation_trace)
    from tools.blind_24_lattice_selector_v7 import (
        BINARY_MODE_COUNT, MODE_CAPACITY, MODE_NAMES, candidate_mode)
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
    from tools.residue_charge_constitution_v1 import (
        CHARGE_CENSUS, dimensionless_electrostatic_relation)
except ImportError:  # direct execution from tools/
    from blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, active_candidates, angles_for_state,
        build_lookahead_prefix, dimensionless_topology_key, validate_sequence)
    from blind_24_lattice_selector_v5 import locally_eligible
    from blind_24_lattice_selector_v6 import (
        ORIENTATION_MODES, interwindow_signed_orientation,
        orientation_orbit_key, selected_orientation_trace)
    from blind_24_lattice_selector_v7 import (
        BINARY_MODE_COUNT, MODE_CAPACITY, MODE_NAMES, candidate_mode)
    from protein_backbone_geometry_v1 import build_backbone_coordinates
    from residue_charge_constitution_v1 import (
        CHARGE_CENSUS, dimensionless_electrostatic_relation)


ORIENTATION_QUARTET = 4


def _ca(atoms) -> np.ndarray:
    return np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)


def generated_prefix_relations(sequence: str, state_path: list[int]):
    """Return hard, charge, packing, and radius relations for one prefix."""
    atoms = build_lookahead_prefix(sequence, state_path)
    coordinates = _ca(atoms)
    active_sequence = sequence[:len(coordinates)]
    topology = dimensionless_topology_key(active_sequence, coordinates)
    charge = dimensionless_electrostatic_relation(
        active_sequence, coordinates)
    return (topology[0], charge, topology[1], topology[2])


def generated_local_relations(sequence: str, state_path: list[int]):
    """Return signed orbit, hard, charge, packing, radius for terminal quartet."""
    prefix_length = len(state_path) + 1
    if prefix_length < ORIENTATION_QUARTET:
        orbit = orientation_orbit_key(sequence, state_path)[0]
        return (orbit, 0, 0.0, 1.0, 0.0)
    atoms = build_lookahead_prefix(sequence, state_path)
    coordinates = _ca(atoms)[-ORIENTATION_QUARTET:]
    active_sequence = sequence[
        prefix_length - ORIENTATION_QUARTET:prefix_length]
    topology = dimensionless_topology_key(active_sequence, coordinates)
    charge = dimensionless_electrostatic_relation(
        active_sequence, coordinates)
    orbit = orientation_orbit_key(sequence, state_path)[0]
    return (orbit, topology[0], charge, topology[1], topology[2])


def select_state_path_v8(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_key": [0, 0.0, 1.0, 0.0, 0, 0, 0.0, 1.0, 0.0],
            "orientation_modes": ORIENTATION_MODES,
            "orientation_trace": [], "mode_capacity": MODE_CAPACITY,
            "mode_balance_trace": [], "charge_census": CHARGE_CENSUS,
            "atoms": atoms,
        }

    beam = [tuple()]
    score_trace = []
    for index in range(len(sequence) - 1):
        by_mode = {name: [] for name in MODE_NAMES}
        for path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                local = generated_local_relations(sequence, list(candidate))
                mode = candidate_mode(sequence, list(candidate))
                by_mode[mode].append((local, candidate))

        retained = []
        mode_row = {}
        for mode in MODE_NAMES:
            eligible = locally_eligible(by_mode[mode], MODE_CAPACITY)
            expanded = []
            for local, candidate in eligible:
                complete = generated_prefix_relations(
                    sequence, list(candidate))
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
        local = generated_local_relations(sequence, list(path))
        complete = generated_prefix_relations(sequence, list(path))
        cross_mode_key = tuple(complete) + tuple(local)
        final_candidates.append((cross_mode_key, path))
    final_candidates.sort(key=lambda item: (item[0], item[1]))
    final_key, active_path = final_candidates[0]
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
        "mode_capacity": MODE_CAPACITY,
        "mode_balance_trace": [row["modes"] for row in score_trace],
        "charge_census": CHARGE_CENSUS,
        "atoms": atoms,
    }
