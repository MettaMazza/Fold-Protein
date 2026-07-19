#!/usr/bin/env python3
"""Selector v11: v10 balance plus backbone hydrogen-bond assembly.

V11 retains the complete v10 constitution and adds one target-incapable,
dimensionless donor/acceptor assembly relation to both the terminal quartet and
the complete generated prefix.  The relation is converted to its within-
frontier ordinal rank with every other objective; it introduces no weight,
reward, cutoff, target, template, or empirical structure.
"""
from __future__ import annotations

try:
    from tools.backbone_hydrogen_bond_constitution_v1 import (
        HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation,
        dimensionless_backbone_hydrogen_bond_relation)
    from tools.blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, active_candidates, angles_for_state,
        build_lookahead_prefix, validate_sequence)
    from tools.blind_24_lattice_selector_v6 import (
        ORIENTATION_MODES, selected_orientation_trace)
    from tools.blind_24_lattice_selector_v7 import (
        MODE_CAPACITY, MODE_NAMES, candidate_mode)
    from tools.blind_24_lattice_selector_v9 import (
        CHARGE_CENSUS, ORIENTATION_QUARTET, STERIC_CENSUS,
        generated_local_relations, generated_prefix_relations)
    from tools.constitutional_rank_balance_v1 import (
        select_balanced, symmetric_ordinal_vectors)
    from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
except ImportError:  # direct execution from tools/
    from backbone_hydrogen_bond_constitution_v1 import (
        HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation,
        dimensionless_backbone_hydrogen_bond_relation)
    from blind_24_lattice_selector_v3 import (
        CANONICAL_STATE, active_candidates, angles_for_state,
        build_lookahead_prefix, validate_sequence)
    from blind_24_lattice_selector_v6 import (
        ORIENTATION_MODES, selected_orientation_trace)
    from blind_24_lattice_selector_v7 import (
        MODE_CAPACITY, MODE_NAMES, candidate_mode)
    from blind_24_lattice_selector_v9 import (
        CHARGE_CENSUS, ORIENTATION_QUARTET, STERIC_CENSUS,
        generated_local_relations, generated_prefix_relations)
    from constitutional_rank_balance_v1 import (
        select_balanced, symmetric_ordinal_vectors)
    from protein_backbone_geometry_v1 import build_backbone_coordinates


CONSTITUTIONAL_OBJECTIVES = 11


def generated_prefix_relations_v11(sequence: str, state_path: list[int]):
    base = generated_prefix_relations(sequence, state_path)
    atoms = build_lookahead_prefix(sequence, state_path)
    active_sequence = sequence[:len(state_path) + 1]
    hydrogen_bond = dimensionless_backbone_hydrogen_bond_relation(
        active_sequence, atoms)
    return tuple(base) + (hydrogen_bond,)


def generated_local_relations_v11(sequence: str, state_path: list[int]):
    base = generated_local_relations(sequence, state_path)
    prefix_length = len(state_path) + 1
    if prefix_length < ORIENTATION_QUARTET:
        return tuple(base) + (0.0,)
    atoms = build_lookahead_prefix(sequence, state_path)
    active_atoms = atoms[-3 * ORIENTATION_QUARTET:]
    active_sequence = sequence[
        prefix_length - ORIENTATION_QUARTET:prefix_length]
    hydrogen_bond = dimensionless_backbone_hydrogen_bond_relation(
        active_sequence, active_atoms)
    return tuple(base) + (hydrogen_bond,)


def _local_row(local: tuple, candidate: tuple[int, ...]):
    return (int(local[1]), (local[0],) + tuple(local[2:]), candidate)


def _combined_row(local: tuple, complete: tuple,
                  candidate: tuple[int, ...]):
    objectives = (local[0],) + tuple(local[2:]) + tuple(complete[1:])
    return (int(complete[0]), objectives, candidate)


def _selected_rank_vector(rows, selected):
    stratum = [row for row in rows if row[0] == selected[0]]
    return list(symmetric_ordinal_vectors(stratum)[selected[2]])


def select_state_path_v11(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_relations": {
                "hard_exclusions": 0,
                "objectives": [0.0] * CONSTITUTIONAL_OBJECTIVES,
                "ordinal_rank_vector": [0] * CONSTITUTIONAL_OBJECTIVES,
                "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(
                    sequence, atoms),
            },
            "orientation_modes": ORIENTATION_MODES,
            "orientation_trace": [], "mode_capacity": MODE_CAPACITY,
            "mode_balance_trace": [], "charge_census": CHARGE_CENSUS,
            "steric_census": STERIC_CENSUS,
            "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
            "atoms": atoms,
        }

    beam = [tuple()]
    score_trace = []
    for index in range(len(sequence) - 1):
        by_mode = {name: [] for name in MODE_NAMES}
        local_by_candidate = {}
        for path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                local = generated_local_relations_v11(
                    sequence, list(candidate))
                local_by_candidate[candidate] = local
                mode = candidate_mode(sequence, list(candidate))
                by_mode[mode].append(_local_row(local, candidate))

        retained = []
        mode_row = {}
        for mode in MODE_NAMES:
            eligible = select_balanced(
                by_mode[mode], MODE_CAPACITY, include_boundary_ties=True)
            combined = []
            for _, _, candidate in eligible:
                complete = generated_prefix_relations_v11(
                    sequence, list(candidate))
                combined.append(_combined_row(
                    local_by_candidate[candidate], complete, candidate))
            held = select_balanced(combined, MODE_CAPACITY)
            retained.extend(row[2] for row in held)
            mode_row[mode] = {
                "expanded": len(by_mode[mode]),
                "locally_eligible": len(eligible),
                "retained": len(held),
                "selected_rank_vectors": [
                    _selected_rank_vector(combined, row) for row in held],
            }
        beam = sorted(retained)
        score_trace.append({
            "active_state": index,
            "mode_capacity": MODE_CAPACITY,
            "modes": mode_row,
            "retained": len(beam),
        })

    final_rows = []
    final_raw = {}
    for path in beam:
        local = generated_local_relations_v11(sequence, list(path))
        complete = generated_prefix_relations_v11(sequence, list(path))
        row = _combined_row(local, complete, path)
        final_rows.append(row)
        final_raw[path] = {"local": list(local), "complete": list(complete)}
    selected = select_balanced(final_rows, 1)[0]
    active_path = selected[2]
    states = list(active_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "score_trace": score_trace,
        "final_relations": {
            "hard_exclusions": selected[0],
            "objectives": list(selected[1]),
            "ordinal_rank_vector": _selected_rank_vector(
                final_rows, selected),
            "raw": final_raw[active_path],
            "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(
                sequence, atoms),
        },
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "mode_capacity": MODE_CAPACITY,
        "mode_balance_trace": [row["modes"] for row in score_trace],
        "charge_census": CHARGE_CENSUS,
        "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "atoms": atoms,
    }
