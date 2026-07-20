#!/usr/bin/env python3
"""Selector V26: joint long-range topology over the V25 search basis.

V26 starts from the sealed V25 complete path and the sealed V23.2 locally
admitted domains.  The existing sequence constraint graph identifies
inter-segment relations whose hydrophobic, opposite-charge, or like-charge
topology remains unresolved on that path.  Weight-free symmetric ordinal
balance retains 24 such segment pairs.  For every retained pair, V26 expands
all 24 x 24 state combinations for every participating residue pair, retains
a 24-path paired-transition frontier, and propagates those joint transitions
through complete-chain beams in both directions.

All counts are inherited: 576 paired states are the 24-axis square and both
topology and path frontiers have the 24-axis capacity.  No target, template,
reward, fitted value, scalar weight, departure penalty, or learned parameter
enters selection.
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
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import (
    sequence_constraint_relations, verify_sequence_constraint_graph)
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


TOPOLOGY_CAPACITY = DOMAIN_CAPACITY


def _active_segment_pairs(sequence: str, seed: tuple[int, ...]):
    graph = sequence_constraint_relations(sequence, _atoms_for_states(sequence, seed))
    rows = []
    for row in graph["segment_pair_rows"]:
        identity = tuple(int(value) for value in row["segments"])
        # A larger current deficit/support conflict is a stronger unresolved
        # command.  Negation lets the unchanged ascending ordinal selector
        # retain those commands without a scalar score or mixed weight.
        objectives = tuple(-int(value) for value in row["objectives"])
        rows.append(((0,), objectives, identity))
    if not rows:
        return (), graph
    selected = select_balanced_hierarchy(rows, min(TOPOLOGY_CAPACITY, len(rows)))
    return tuple(row[2] for row in selected), graph


def _segment_lookup(segments):
    return {index: segment for index, segment in enumerate(segments)}


def _paired_transition_frontier(seed, domains, left_segment, right_segment,
                                evaluator):
    candidates = {seed}
    residue_pairs = 0
    for left in left_segment:
        for right in right_segment:
            if abs(right - left) < 2:
                continue
            residue_pairs += 1
            for left_state in domains[left]:
                for right_state in domains[right]:
                    candidate = list(seed)
                    candidate[left] = left_state
                    candidate[right] = right_state
                    candidates.add(tuple(candidate))
    selected = _select_unique(
        [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
    return tuple(row[2] for row in selected), {
        "residue_pair_count": residue_pairs,
        "expanded_unique_paths": len(candidates),
        "retained_paths": len(selected),
        "best_hard_vector": list(selected[0][0]),
    }


def _apply_parent_delta(path, alternative, seed):
    candidate = list(path)
    for residue, (state, parent_state) in enumerate(zip(alternative, seed)):
        if state != parent_state:
            candidate[residue] = state
    return tuple(candidate)


def _assemble_topology(seed, topology_pairs, alternatives, evaluator, direction):
    frontier = (seed,)
    trace = []
    ordered = topology_pairs if direction == "forward" else tuple(reversed(topology_pairs))
    for pair in ordered:
        candidates = set()
        for path in frontier:
            for alternative in alternatives[pair]:
                candidates.add(_apply_parent_delta(path, alternative, seed))
        selected = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in selected)
        trace.append({
            "direction": direction,
            "segment_pair": list(pair),
            "expanded_unique_paths": len(candidates),
            "retained_paths": len(frontier),
            "parent_path_present": seed in candidates,
            "parent_path_retained": seed in frontier,
            "best_hard_vector": list(selected[0][0]),
        })
    return frontier, trace


def select_state_path_v26(sequence: str, parent_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in parent_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("V26 requires a valid sealed V25 parent path")
    domains = _validated_domains(sequence, domain_trace)
    segments = _segments(len(sequence) - 1)
    by_index = _segment_lookup(segments)
    topology_pairs, parent_graph = _active_segment_pairs(sequence, seed)
    topology_pairs = tuple(
        pair for pair in topology_pairs
        if pair[0] in by_index and pair[1] in by_index)

    evaluator = _WholeChainEvaluator(sequence)
    alternatives, topology_trace = {}, []
    for pair in topology_pairs:
        held, trace = _paired_transition_frontier(
            seed, domains, by_index[pair[0]], by_index[pair[1]], evaluator)
        if len(held) != FRONTIER_CAPACITY:
            raise RuntimeError("V26 paired transition frontier did not close")
        alternatives[pair] = held
        topology_trace.append({
            "segment_pair": list(pair),
            "paired_state_count_per_residue_pair": DOMAIN_STATE_COUNT,
            **trace,
        })

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
