#!/usr/bin/env python3
"""Selector v21: explicit graph contact topology in global assembly.

V21 preserves V13 local candidate eligibility exactly. At complete-prefix
assembly it retains V19's hierarchical hard exclusions and adds the negative
of the exact fold-to-One atom-contact census as one permutation-invariant
objective, so the ordinal minimax assembly favours more explicit contacts
without a fitted weight or a commensurate scalar combination.
"""
from __future__ import annotations

from tools.backbone_hydrogen_bond_constitution_v1 import (
    HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation)
from tools.backbone_hydrogen_bond_constitution_v2 import (
    TOPOLOGY_HYDROGEN_BOND_CENSUS, topology_backbone_hydrogen_bond_relation)
from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE, active_candidates, angles_for_state, build_lookahead_prefix,
    validate_sequence)
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v7 import MODE_CAPACITY, MODE_NAMES, candidate_mode
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v19 import (
    HARD_EXCLUSION_STRATA, _combined_row, _local_row, _selected_rank_vector,
    generated_local_relations_v19, generated_prefix_relations_v19)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from tools.sidechain_graph_contact_topology_v1 import (
    CONTACT_SHELL, sidechain_graph_contact_relation)
from tools.sidechain_graph_spatial_exclusion_v1 import (
    SIDECHAIN_GRAPH_SPATIAL_CENSUS, sidechain_graph_spatial_exclusion_relation)


CONSTITUTIONAL_OBJECTIVES = 16


def generated_prefix_relations_v21(sequence: str, state_path: list[int]):
    base = generated_prefix_relations_v19(sequence, state_path)
    atoms = build_lookahead_prefix(sequence, state_path)
    active_sequence = sequence[:len(state_path) + 1]
    contact = sidechain_graph_contact_relation(active_sequence, atoms)
    return tuple(base) + (-int(contact["atom_contact_count"]),)


def select_state_path_v21(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "score_trace": [],
            "final_relations": {
                "hard_exclusions": 0,
                "hard_exclusion_vector": [0, 0],
                "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
                "objectives": [0.0] * CONSTITUTIONAL_OBJECTIVES,
                "ordinal_rank_vector": [0] * CONSTITUTIONAL_OBJECTIVES,
                "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
                "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
                "sidechain_graph_spatial_exclusion": sidechain_graph_spatial_exclusion_relation(sequence, atoms),
                "sidechain_graph_contact_topology": sidechain_graph_contact_relation(sequence, atoms),
            },
            "orientation_modes": ORIENTATION_MODES,
            "orientation_trace": [], "mode_capacity": MODE_CAPACITY,
            "mode_balance_trace": [], "charge_census": CHARGE_CENSUS,
            "steric_census": STERIC_CENSUS,
            "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
            "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
            "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
            "sidechain_graph_contact_census": CONTACT_SHELL,
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
                local = generated_local_relations_v19(sequence, list(candidate))
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
                complete = generated_prefix_relations_v21(sequence, list(candidate))
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
        local = generated_local_relations_v19(sequence, list(path))
        complete = generated_prefix_relations_v21(sequence, list(path))
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
            "sidechain_graph_contact_topology": sidechain_graph_contact_relation(sequence, atoms),
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
        "sidechain_graph_contact_census": CONTACT_SHELL,
        "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
        "local_graph_pruning": False,
        "atoms": atoms,
    }
