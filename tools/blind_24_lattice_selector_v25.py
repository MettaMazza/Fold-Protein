#!/usr/bin/env python3
"""Selector V25: parent-anchored constitutional coordinate beam.

V24 showed that replacing complete four-residue tuples can erase a stronger
locally admitted whole-chain path.  V25 therefore changes the search basis,
not the constitutional judge.  Starting from the sealed V23.2 result, every
four-residue unit exposes the complete set of one-coordinate transitions into
its 24-state locally admitted domains, together with the unchanged path.  A
24-path beam propagates those transitions independently in both chain
directions and the existing rich V19/global constitution reconciles the two
complete-chain frontiers.

The elementary move is one generated coordinate inside the already derived
four-residue unit.  The domain and beam capacities remain the counted 24-state
lattice axis.  There is no departure score, continuity penalty, target,
template, reward, fitted value, scalar weight, or learned parameter.
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
    _WholeChainEvaluator, _rich_final_row, _segments, _select_unique)
from tools.blind_24_lattice_selector_v24 import _validated_domains
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _coordinate_candidates(path: tuple[int, ...], segment, domains):
    """Enumerate the unchanged path and every admitted one-coordinate move."""
    candidates = {path}
    for residue in segment:
        for state in domains[residue]:
            candidate = list(path)
            candidate[residue] = state
            candidates.add(tuple(candidate))
    return tuple(sorted(candidates))


def _coordinate_beam(seed, domains, segments, evaluator, direction):
    frontier = (seed,)
    trace = []
    ordered = segments if direction == "forward" else tuple(reversed(segments))
    for segment in ordered:
        paths = set()
        for path in frontier:
            paths.update(_coordinate_candidates(path, segment, domains))
        selected = _select_unique(
            [evaluator.row(path) for path in sorted(paths)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in selected)
        trace.append({
            "direction": direction,
            "segment_residues": [residue + 1 for residue in segment],
            "expanded_unique_paths": len(paths),
            "retained_paths": len(frontier),
            "parent_path_present": seed in paths,
            "parent_path_retained": seed in frontier,
            "best_hard_vector": list(selected[0][0]),
        })
    return frontier, trace


def select_state_path_v25(sequence: str, parent_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in parent_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("V25 requires a valid sealed V23.2 parent path")
    domains = _validated_domains(sequence, domain_trace)
    segments = _segments(len(sequence) - 1)
    evaluator = _WholeChainEvaluator(sequence)
    forward, forward_trace = _coordinate_beam(
        seed, domains, segments, evaluator, "forward")
    reverse, reverse_trace = _coordinate_beam(
        seed, domains, segments, evaluator, "reverse")

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
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "unique_input_paths": len(candidates),
            "retained_paths": len(reconciliation),
            "parent_path_retained": any(row[2] == seed for row in reconciliation),
        },
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
