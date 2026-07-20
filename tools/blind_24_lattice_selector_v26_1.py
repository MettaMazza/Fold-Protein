#!/usr/bin/env python3
"""Selector V26.1: focal admission for V26 joint topology transitions.

V26.1 preserves the complete V26 paired-state expansion and bidirectional
assembly.  It corrects one ordering: each 576-state residue-pair domain is
first admitted by the exact segment-pair relation that caused its expansion;
only those focal alternatives enter whole-chain constitutional balance.  This
is hierarchical local-to-global admission, not a target-derived score change.
"""
from __future__ import annotations

import time

from tools.backbone_hydrogen_bond_constitution_v1 import backbone_hydrogen_bond_relation
from tools.backbone_hydrogen_bond_constitution_v2 import topology_backbone_hydrogen_bond_relation
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, HYDROGEN_BOND_CENSUS, SEGMENT_RESIDUES,
    SIDECHAIN_GRAPH_SPATIAL_CENSUS, TOPOLOGY_HYDROGEN_BOND_CENSUS,
    _WholeChainEvaluator, _atoms_for_states, _rich_final_row, _segments,
    _select_unique)
from tools.blind_24_lattice_selector_v24 import _validated_domains
from tools.blind_24_lattice_selector_v26 import (
    TOPOLOGY_CAPACITY, _active_segment_pairs, _assemble_topology,
    _segment_lookup)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import (
    sequence_constraint_relations, verify_sequence_constraint_graph)
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _focal_and_global_rows(sequence, states, segment_pair):
    graph = sequence_constraint_relations(
        sequence, _atoms_for_states(sequence, states), include_rows=True)
    focal = next(
        row for row in graph["segment_pair_rows"]
        if tuple(row["segments"]) == segment_pair)
    hard = (int(graph["backbone_exclusions"]),)
    focal_row = (hard, tuple(focal["objectives"]), states)
    global_row = (
        hard, tuple(graph["objectives"] + graph["segment_pair_objectives"]), states)
    return focal_row, global_row


def _focally_admitted_transition_frontier(sequence, seed, domains,
                                           left_segment, right_segment,
                                           segment_pair):
    admitted_global = []
    residue_pairs = 0
    evaluations = 0
    for left in left_segment:
        for right in right_segment:
            if abs(right - left) < 2:
                continue
            residue_pairs += 1
            focal_rows, global_by_state = [], {}
            for left_state in domains[left]:
                for right_state in domains[right]:
                    candidate = list(seed)
                    candidate[left] = left_state
                    candidate[right] = right_state
                    states = tuple(candidate)
                    focal_row, global_row = _focal_and_global_rows(
                        sequence, states, segment_pair)
                    focal_rows.append(focal_row)
                    global_by_state[states] = global_row
                    evaluations += 1
            focal_held = _select_unique(focal_rows, FRONTIER_CAPACITY)
            admitted_global.extend(global_by_state[row[2]] for row in focal_held)
    seed_focal, seed_global = _focal_and_global_rows(sequence, seed, segment_pair)
    del seed_focal
    evaluations += 1
    selected = _select_unique([*admitted_global, seed_global], FRONTIER_CAPACITY)
    return tuple(row[2] for row in selected), {
        "residue_pair_count": residue_pairs,
        "expanded_paired_paths": residue_pairs * DOMAIN_STATE_COUNT,
        "focally_admitted_paths": len(admitted_global),
        "retained_paths": len(selected),
        "best_hard_vector": list(selected[0][0]),
        "focal_evaluations": evaluations,
    }


def select_state_path_v26_1(sequence: str, parent_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in parent_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("V26.1 requires a valid sealed V25 parent path")
    domains = _validated_domains(sequence, domain_trace)
    segments = _segments(len(sequence) - 1)
    by_index = _segment_lookup(segments)
    topology_pairs, parent_graph = _active_segment_pairs(sequence, seed)
    topology_pairs = tuple(
        pair for pair in topology_pairs
        if pair[0] in by_index and pair[1] in by_index)

    alternatives, topology_trace, focal_evaluations = {}, [], 0
    for pair in topology_pairs:
        held, trace = _focally_admitted_transition_frontier(
            sequence, seed, domains, by_index[pair[0]], by_index[pair[1]], pair)
        alternatives[pair] = held
        focal_evaluations += trace["focal_evaluations"]
        topology_trace.append({
            "segment_pair": list(pair),
            "paired_state_count_per_residue_pair": DOMAIN_STATE_COUNT,
            "admission": "focal segment-pair relation then complete-chain balance",
            **trace,
        })

    evaluator = _WholeChainEvaluator(sequence)
    forward, forward_trace = _assemble_topology(
        seed, topology_pairs, alternatives, evaluator, "forward")
    reverse, reverse_trace = _assemble_topology(
        seed, topology_pairs, alternatives, evaluator, "reverse")
    candidates = {*forward, *reverse, seed}
    reconciliation = _select_unique(
        [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
    rich_rows, raw = [], {}
    for _, _, states in reconciliation:
        row, atoms, graph, local, complete = _rich_final_row(sequence, states)
        rich_rows.append(row)
        raw[states] = (atoms, graph, local, complete)
    selected = select_balanced_hierarchy(rich_rows, 1)[0]
    states = selected[2]
    atoms, graph, local, complete = raw[states]
    graph_spatial = sidechain_graph_spatial_exclusion_relation(sequence, atoms)
    departures = sum(left != right for left, right in zip(states, seed))
    return {
        "states": list(states), "seed_states": list(seed),
        "parent_departures": departures,
        "topology_pairs": [list(pair) for pair in topology_pairs],
        "topology_trace": topology_trace,
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "unique_input_paths": len(candidates),
            "retained_paths": len(reconciliation),
            "parent_path_retained": any(row[2] == seed for row in reconciliation),
        },
        "parent_constraint_graph": parent_graph,
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "objectives": list(selected[1]),
            "raw": {"local": list(local), "complete": list(complete)},
            "constraint_graph": graph,
            "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
            "sidechain_graph_spatial_exclusion": graph_spatial,
        },
        "constraint_graph_census": verify_sequence_constraint_graph(sequence),
        "domain_state_count": DOMAIN_STATE_COUNT,
        "domain_capacity": DOMAIN_CAPACITY,
        "topology_capacity": TOPOLOGY_CAPACITY,
        "frontier_capacity": FRONTIER_CAPACITY,
        "segment_residues": SEGMENT_RESIDUES,
        "segment_count": len(segments),
        "focal_evaluations": focal_evaluations,
        "whole_chain_evaluations": evaluator.evaluations,
        "whole_chain_cache_hits": evaluator.cache_hits,
        "runtime_seconds": time.perf_counter() - started,
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "charge_census": CHARGE_CENSUS, "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
        "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
        "atoms": atoms,
    }
