#!/usr/bin/env python3
"""Selector v20: exact graph-encounter child stratum in global assembly.

V20 preserves V13 local candidate eligibility exactly. At complete-prefix
assembly it refines V19's ordered hard vector into parent backbone exclusions,
attached side-chain graph pair exclusions, and the exact atom encounters inside
those excluded pairs. Encounter count cannot trade against either parent fact;
it acts only inside an identical (backbone, graph-pair) stratum.
"""
from __future__ import annotations

import numpy as np

from tools.backbone_hydrogen_bond_constitution_v1 import (
    HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation,
    dimensionless_backbone_hydrogen_bond_relation)
from tools.backbone_hydrogen_bond_constitution_v2 import (
    TOPOLOGY_HYDROGEN_BOND_CENSUS,
    dimensionless_topology_hydrogen_bond_relations,
    topology_backbone_hydrogen_bond_relation)
from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE, active_candidates, angles_for_state,
    build_lookahead_prefix, dimensionless_topology_key, validate_sequence)
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v7 import MODE_CAPACITY, MODE_NAMES, candidate_mode
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v13 import generated_local_relations_v13
from tools.blind_24_lattice_selector_v18 import CONSTITUTIONAL_OBJECTIVES
from tools.constitutional_lexicographic_exclusion_v1 import (
    select_balanced_hierarchy, symmetric_ordinal_vectors)
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from tools.residue_charge_constitution_v1 import dimensionless_electrostatic_relation
from tools.residue_steric_constitution_v1 import dimensionless_sidechain_crowding_relation
from tools.sidechain_graph_spatial_exclusion_v1 import (
    SIDECHAIN_GRAPH_SPATIAL_CENSUS,
    sidechain_graph_spatial_exclusion_relation)


HARD_EXCLUSION_STRATA = (
    "backbone", "sidechain_graph_pair", "sidechain_graph_atom_encounter")


def _ca(atoms) -> np.ndarray:
    return np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)


def generated_local_relations_v20(sequence: str, state_path: list[int]):
    local = generated_local_relations_v13(sequence, state_path)
    return (local[0], (int(local[1]), 0, 0)) + tuple(local[2:])


def generated_prefix_relations_v20(sequence: str, state_path: list[int]):
    atoms = build_lookahead_prefix(sequence, state_path)
    coordinates = _ca(atoms)
    active_sequence = sequence[:len(coordinates)]
    topology = dimensionless_topology_key(active_sequence, coordinates)
    spatial = sidechain_graph_spatial_exclusion_relation(active_sequence, atoms)
    hard = (
        int(topology[0]), int(spatial["hard_exclusions"]),
        int(spatial["atom_encounter_count"]))
    steric = dimensionless_sidechain_crowding_relation(active_sequence, coordinates)
    charge = dimensionless_electrostatic_relation(active_sequence, coordinates)
    base = (hard, steric, charge, topology[1], topology[2])
    hydrogen_topology = dimensionless_topology_hydrogen_bond_relations(
        active_sequence, atoms)
    retained = dimensionless_backbone_hydrogen_bond_relation(active_sequence, atoms)
    return tuple(base) + tuple(hydrogen_topology) + (retained,)


def _local_row(local, candidate):
    return (tuple(local[1]), (local[0],) + tuple(local[2:]), candidate)


def _combined_row(local, complete, candidate):
    objectives = (local[0],) + tuple(local[2:]) + tuple(complete[1:])
    return (tuple(complete[0]), objectives, candidate)


def _selected_rank_vector(rows, selected):
    stratum = [row for row in rows if row[0] == selected[0]]
    return list(symmetric_ordinal_vectors(stratum)[selected[2]])


def select_state_path_v20(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_relations": {
                "hard_exclusions": 0,
                "hard_exclusion_vector": [0, 0, 0],
                "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
                "objectives": [0.0] * CONSTITUTIONAL_OBJECTIVES,
                "ordinal_rank_vector": [0] * CONSTITUTIONAL_OBJECTIVES,
                "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
                "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
                "sidechain_graph_spatial_exclusion": sidechain_graph_spatial_exclusion_relation(sequence, atoms),
            },
            "orientation_modes": ORIENTATION_MODES,
            "orientation_trace": [], "mode_capacity": MODE_CAPACITY,
            "mode_balance_trace": [], "charge_census": CHARGE_CENSUS,
            "steric_census": STERIC_CENSUS,
            "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
            "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
            "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "local_graph_pruning": False,
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
                local = generated_local_relations_v20(sequence, list(candidate))
                local_by_candidate[candidate] = local
                by_mode[candidate_mode(sequence, list(candidate))].append(
                    _local_row(local, candidate))
        retained = []
        mode_row = {}
        for mode in MODE_NAMES:
            eligible = select_balanced_hierarchy(
                by_mode[mode], MODE_CAPACITY, include_boundary_ties=True)
            combined = []
            for _, _, candidate in eligible:
                complete = generated_prefix_relations_v20(sequence, list(candidate))
                combined.append(_combined_row(
                    local_by_candidate[candidate], complete, candidate))
            held = select_balanced_hierarchy(combined, MODE_CAPACITY)
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
            "active_state": index, "mode_capacity": MODE_CAPACITY,
            "modes": mode_row, "retained": len(beam)})
    final_rows = []
    final_raw = {}
    for path in beam:
        local = generated_local_relations_v20(sequence, list(path))
        complete = generated_prefix_relations_v20(sequence, list(path))
        row = _combined_row(local, complete, path)
        final_rows.append(row)
        final_raw[path] = {"local": list(local), "complete": list(complete)}
    selected = select_balanced_hierarchy(final_rows, 1)[0]
    active_path = selected[2]
    states = list(active_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "score_trace": score_trace,
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "objectives": list(selected[1]),
            "ordinal_rank_vector": _selected_rank_vector(final_rows, selected),
            "raw": final_raw[active_path],
            "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
            "sidechain_graph_spatial_exclusion": sidechain_graph_spatial_exclusion_relation(sequence, atoms),
        },
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "mode_capacity": MODE_CAPACITY,
        "mode_balance_trace": [row["modes"] for row in score_trace],
        "charge_census": CHARGE_CENSUS,
        "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
        "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
        "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        "local_graph_pruning": False,
        "atoms": atoms,
    }
