#!/usr/bin/env python3
"""Selector v24.1: boundary-closed coherent segment assembly.

V24.1 preserves V24's 24 coherent tuples per four-residue segment and repairs
the measured boundary defect: whenever a tuple enters a whole-chain path, all
local windows crossing either segment boundary are re-evaluated in that path's
current context. Their unchanged V19-wrapped V13 hard/local relations precede
the complete-chain row. Final forward/reverse reconciliation re-evaluates
every overlapping local window across the complete path.
"""
from __future__ import annotations

import time

from tools.backbone_hydrogen_bond_constitution_v1 import backbone_hydrogen_bond_relation
from tools.backbone_hydrogen_bond_constitution_v2 import topology_backbone_hydrogen_bond_relation
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v19 import generated_local_relations_v19
from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY, HARD_EXCLUSION_STRATA,
    HYDROGEN_BOND_CENSUS, SEGMENT_RESIDUES, SIDECHAIN_GRAPH_SPATIAL_CENSUS,
    TOPOLOGY_HYDROGEN_BOND_CENSUS, _WholeChainEvaluator, _rich_final_row,
    _segments, _select_unique)
from tools.blind_24_lattice_selector_v24 import (
    _coherent_segment_frontier, _validated_domains)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _local_context_row(sequence: str, states: tuple[int, ...], active_indices):
    relations = [generated_local_relations_v19(
        sequence, list(states[:index + 1])) for index in active_indices]
    hard_dimension = len(relations[0][1]) if relations else 3
    hard = tuple(sum(int(row[1][axis]) for row in relations)
                 for axis in range(hard_dimension))
    objectives = tuple(value for row in relations
                       for value in ((row[0],) + tuple(row[2:])))
    return hard, objectives


def _boundary_indices(segment, active_count):
    start, end = segment[0], segment[-1]
    return tuple(sorted({index for index in (
        start, start + 1, start + 2, end, end + 1, end + 2)
        if 0 <= index < active_count}))


def _contextual_row(sequence, states, evaluator, active_indices):
    local_hard, local_objectives = _local_context_row(
        sequence, states, active_indices)
    global_row = evaluator.row(states)
    return (local_hard + tuple(global_row[0]),
            local_objectives + tuple(global_row[1]), states)


def _assemble_boundary_closed(sequence, seed, segments, alternatives,
                              evaluator, direction):
    frontier = [seed]
    trace = []
    ordered = segments if direction == "forward" else tuple(reversed(segments))
    for segment in ordered:
        indices = _boundary_indices(segment, len(sequence) - 1)
        rows = []
        for path in frontier:
            for choice in alternatives[segment]:
                candidate = list(path)
                for residue, state in zip(segment, choice):
                    candidate[residue] = state
                rows.append(_contextual_row(
                    sequence, tuple(candidate), evaluator, indices))
        selected = _select_unique(rows, FRONTIER_CAPACITY)
        frontier = [row[2] for row in selected]
        trace.append({
            "direction": direction,
            "segment_residues": [residue + 1 for residue in segment],
            "boundary_active_states": [index + 1 for index in indices],
            "expanded_unique_paths": len({row[2] for row in rows}),
            "retained_paths": len(frontier),
            "best_context_hard_vector": list(selected[0][0]),
        })
    return tuple(frontier), trace


def select_state_path_v24_1(sequence: str, seed_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in seed_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("V24.1 requires a valid registered complete-sequence seed")
    domains = _validated_domains(sequence, domain_trace)
    segments = _segments(len(sequence) - 1)
    alternatives = {}
    segment_generation_trace = []
    for segment in segments:
        held, trace = _coherent_segment_frontier(sequence, seed, domains, segment)
        alternatives[segment] = held
        segment_generation_trace.append({
            "segment_residues": [residue + 1 for residue in segment],
            "retained_tuple_count": len(held), "construction_trace": trace})
    evaluator = _WholeChainEvaluator(sequence)
    forward, forward_trace = _assemble_boundary_closed(
        sequence, seed, segments, alternatives, evaluator, "forward")
    reverse, reverse_trace = _assemble_boundary_closed(
        sequence, seed, segments, alternatives, evaluator, "reverse")
    all_indices = tuple(range(len(sequence) - 1))
    reconciliation = _select_unique([
        _contextual_row(sequence, path, evaluator, all_indices)
        for path in (*forward, *reverse, seed)], FRONTIER_CAPACITY)
    rich_rows = []
    raw = {}
    for _, _, states in reconciliation:
        base, atoms, graph, local, complete = _rich_final_row(sequence, states)
        local_hard, local_objectives = _local_context_row(
            sequence, states, all_indices)
        row = (local_hard + tuple(base[0]),
               local_objectives + tuple(base[1]), states)
        rich_rows.append(row)
        raw[states] = (atoms, graph, local, complete)
    selected = select_balanced_hierarchy(rich_rows, 1)[0]
    states = selected[2]
    atoms, graph, local, complete = raw[states]
    graph_spatial = sidechain_graph_spatial_exclusion_relation(sequence, atoms)
    return {
        "states": list(states), "seed_states": list(seed),
        "parent_departures": sum(a != b for a, b in zip(states, seed)),
        "segment_generation_trace": segment_generation_trace,
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "unique_input_paths": len({*forward, *reverse, seed}),
            "retained_paths": len(reconciliation),
            "complete_local_window_count": len(all_indices),
        },
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": [
                "local_backbone", "local_graph",
                *HARD_EXCLUSION_STRATA],
            "objectives": list(selected[1]),
            "raw": {"local": list(local), "complete": list(complete)},
            "constraint_graph": graph,
            "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
            "sidechain_graph_spatial_exclusion": graph_spatial,
        },
        "constraint_graph_census": verify_sequence_constraint_graph(sequence),
        "domain_state_count": DOMAIN_STATE_COUNT, "domain_capacity": DOMAIN_CAPACITY,
        "frontier_capacity": FRONTIER_CAPACITY, "segment_residues": SEGMENT_RESIDUES,
        "segment_count": len(segments), "whole_chain_evaluations": evaluator.evaluations,
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
