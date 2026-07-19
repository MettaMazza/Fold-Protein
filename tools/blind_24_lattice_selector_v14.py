#!/usr/bin/env python3
"""Selector v14: retain v13 and add exact hydrogen-bond continuity.

V14 preserves every v13 constitutional objective and adds two independent
integer relations: consecutive alpha hydrogen bonds and consecutive
inter-strand hydrogen bonds. Both are derived from the exact residue successor
over the already assembled unit-capacity pairs. No objective is duplicated and
no weight, cutoff, target, reward, template, or learned quantity is introduced.
"""
from __future__ import annotations

import numpy as np

from tools.backbone_hydrogen_bond_constitution_v1 import (
    HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation,
    dimensionless_backbone_hydrogen_bond_relation)
from tools.backbone_hydrogen_bond_constitution_v2 import (
    TOPOLOGY_HYDROGEN_BOND_CENSUS,
    topology_backbone_hydrogen_bond_relation)
from tools.backbone_hydrogen_bond_continuity_v1 import (
    HYDROGEN_BOND_CONTINUITY_CENSUS,
    backbone_hydrogen_bond_continuity_relation, continuity_from_pairs)
from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE, active_candidates, angles_for_state,
    build_lookahead_prefix, dimensionless_topology_key, validate_sequence)
from tools.blind_24_lattice_selector_v6 import (
    ORIENTATION_MODES, selected_orientation_trace)
from tools.blind_24_lattice_selector_v7 import (
    MODE_CAPACITY, MODE_NAMES, candidate_mode)
from tools.blind_24_lattice_selector_v9 import (
    CHARGE_CENSUS, STERIC_CENSUS)
from tools.blind_24_lattice_selector_v13 import (
    _combined_row, _local_row, _selected_rank_vector)
from tools.blind_24_lattice_selector_v13_single_build_candidate import (
    generated_local_relations_v13_single_build,
    select_state_path_v13_single_build)
from tools.constitutional_rank_balance_v1 import select_balanced
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from tools.residue_charge_constitution_v1 import (
    dimensionless_electrostatic_relation)
from tools.residue_steric_constitution_v1 import (
    dimensionless_sidechain_crowding_relation)


CONSTITUTIONAL_OBJECTIVES = 17


def _ca(atoms) -> np.ndarray:
    return np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"],
        dtype=float)


def generated_prefix_relations_v14(sequence: str, state_path: list[int]):
    atoms = build_lookahead_prefix(sequence, state_path)
    coordinates = _ca(atoms)
    active_sequence = sequence[:len(coordinates)]
    topology = dimensionless_topology_key(active_sequence, coordinates)
    steric = dimensionless_sidechain_crowding_relation(
        active_sequence, coordinates)
    charge = dimensionless_electrostatic_relation(
        active_sequence, coordinates)
    base = (topology[0], steric, charge, topology[1], topology[2])

    assembled = topology_backbone_hydrogen_bond_relation(
        active_sequence, atoms)
    topology_relations = tuple(
        float(assembled["relations"][name])
        for name in ("alpha", "interstrand"))
    retained = dimensionless_backbone_hydrogen_bond_relation(
        active_sequence, atoms)
    continuity = continuity_from_pairs(assembled["pairs"])
    continuity_relations = tuple(
        int(continuity["relations"][name])
        for name in ("alpha", "interstrand"))
    return (tuple(base) + topology_relations + (retained,)
            + continuity_relations)


def select_state_path_v14(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) == 1:
        result = select_state_path_v13_single_build(sequence)
        result["final_relations"]["objectives"].extend([0, 0])
        result["final_relations"]["ordinal_rank_vector"].extend([0, 0])
        result["final_relations"]["hydrogen_bond_continuity"] = \
            backbone_hydrogen_bond_continuity_relation(
                sequence, result["atoms"])
        result["hydrogen_bond_continuity_census"] = \
            HYDROGEN_BOND_CONTINUITY_CENSUS
        return result

    beam = [tuple()]
    score_trace = []
    for index in range(len(sequence) - 1):
        by_mode = {name: [] for name in MODE_NAMES}
        local_by_candidate = {}
        for path in beam:
            for state in active_candidates(index, len(sequence)):
                candidate = tuple(path) + (state,)
                local = generated_local_relations_v13_single_build(
                    sequence, list(candidate))
                local_by_candidate[candidate] = local
                by_mode[candidate_mode(sequence, list(candidate))].append(
                    _local_row(local, candidate))

        retained = []
        mode_row = {}
        for mode in MODE_NAMES:
            eligible = select_balanced(
                by_mode[mode], MODE_CAPACITY, include_boundary_ties=True)
            combined = []
            for _, _, candidate in eligible:
                complete = generated_prefix_relations_v14(
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
        local = generated_local_relations_v13_single_build(
            sequence, list(path))
        complete = generated_prefix_relations_v14(sequence, list(path))
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
            "hydrogen_bond_assembly":
                backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_topologies":
                topology_backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_continuity":
                backbone_hydrogen_bond_continuity_relation(sequence, atoms),
        },
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "mode_capacity": MODE_CAPACITY,
        "mode_balance_trace": [row["modes"] for row in score_trace],
        "charge_census": CHARGE_CENSUS,
        "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
        "hydrogen_bond_continuity_census":
            HYDROGEN_BOND_CONTINUITY_CENSUS,
        "atoms": atoms,
    }
