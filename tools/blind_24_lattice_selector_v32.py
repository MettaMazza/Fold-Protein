#!/usr/bin/env python3
"""Selector V32: constitutional cross-topology consensus.

V31 independently constructs all counted degree families but allows the final
physical-objective reconciliation to erase family provenance.  V32 retains
the same complete topology construction, then derives for every candidate its
minimum counted state distance to each complete family frontier.  The three
distances enter one permutation-invariant consensus relation.  Only the 24
consensus paths enter the established whole-chain constitution.

No family receives a scalar weight, quota, lock or reward. No target,
template, fitted cutoff or trained parameter enters construction or selection.
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
    _rich_final_row, _select_unique)
from tools.blind_24_lattice_selector_v24 import _validated_domains
from tools.blind_24_lattice_selector_v29 import _assemble_edges
from tools.blind_24_lattice_selector_v31 import _BoundedTopologyEvaluator
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation
from tools.tertiary_segment_body_constitution_v3 import (
    DEGREE_FRONTIER, bounded_tertiary_relation, build_bounded_tertiary_topology,
    verify_tertiary_topology_frontier)


def _state_distance(left, right):
    return sum(a != b for a, b in zip(left, right))


def _consensus_relation(states, topology_frontiers):
    distances = tuple(min(_state_distance(states, path) for path in frontier)
                      for frontier in topology_frontiers)
    return {"family_minimum_state_distances": list(distances),
            "worst_family_distance": max(distances),
            "total_family_distance": sum(distances)}


def select_state_path_v32(sequence: str, v25_states, v26_1_states,
                          v27_states, v28_states, v29_states, v30_states,
                          domain_trace) -> dict:
    sequence, started = validate_sequence(sequence), time.perf_counter()
    names = ("v25", "v26_1", "v27", "v28", "v29", "v30")
    branches = tuple(tuple(int(state) for state in states) for states in (
        v25_states, v26_1_states, v27_states, v28_states, v29_states, v30_states))
    for name, states in zip(names, branches):
        if (len(states) != len(sequence) or states[-1] != CANONICAL_STATE
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise ValueError(f"V32 requires a valid sealed {name.upper()} branch")
    domains = _validated_domains(sequence, domain_trace)
    seed = tuple(dict.fromkeys(branches))
    topology_traces, topology_frontiers, evaluators = [], [], {}
    all_candidates = set(branches)
    for capacity in DEGREE_FRONTIER:
        topology = build_bounded_tertiary_topology(sequence, capacity)
        evaluator = _BoundedTopologyEvaluator(sequence, capacity)
        evaluators[capacity] = evaluator
        forward, forward_trace = _assemble_edges(
            seed, topology, branches, domains, evaluator, "forward")
        reverse, reverse_trace = _assemble_edges(
            seed, topology, branches, domains, evaluator, "reverse")
        candidates = {*forward, *reverse, *branches}
        retained_rows = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in retained_rows)
        topology_frontiers.append(frontier)
        all_candidates.update(frontier)
        topology_traces.append({
            "degree_capacity": capacity, "topology": list(topology),
            "forward_trace": forward_trace, "reverse_trace": reverse_trace,
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "reconciliation_inputs": len(candidates),
            "retained_paths": len(frontier),
            "branch_retention": [branch in frontier for branch in branches],
        })

    topology_frontiers = tuple(topology_frontiers)
    consensus_raw = {}
    consensus_rows = []
    for states in sorted(all_candidates):
        relation = _consensus_relation(states, topology_frontiers)
        consensus_raw[states] = relation
        consensus_rows.append(((0,), tuple(
            relation["family_minimum_state_distances"]), states))
    consensus_frontier = select_balanced_hierarchy(
        consensus_rows, FRONTIER_CAPACITY)

    rich_rows, raw = [], {}
    for _, _, states in consensus_frontier:
        base, atoms, graph, local, complete = _rich_final_row(sequence, states)
        rich_rows.append(base)
        raw[states] = (atoms, graph, local, complete)
    final_frontier = select_balanced_hierarchy(rich_rows, FRONTIER_CAPACITY)
    selected = final_frontier[0]
    states = selected[2]
    atoms, graph, local, complete = raw[states]
    relations = {capacity: bounded_tertiary_relation(sequence, atoms, capacity)
                 for capacity in DEGREE_FRONTIER}

    def membership(path):
        return [capacity for capacity, frontier in zip(DEGREE_FRONTIER, topology_frontiers)
                if path in frontier]

    return {
        "states": list(states),
        **{name + "_states": list(branch) for name, branch in zip(names, branches)},
        **{name + "_departures": _state_distance(states, branch)
           for name, branch in zip(names, branches)},
        "tertiary_census": verify_tertiary_topology_frontier(sequence),
        "topology_traces": topology_traces,
        "consensus": {
            "candidate_count": len(all_candidates),
            "retained_paths": len(consensus_frontier),
            "selected_relation": consensus_raw[states],
            "retained_relations": [consensus_raw[row[2]] for row in consensus_frontier],
            "retained_family_membership": [membership(row[2])
                                            for row in consensus_frontier],
            "selected_family_membership": membership(states),
            "family_order": list(DEGREE_FRONTIER),
        },
        "reconciliation": {
            "retained_paths": len(final_frontier),
            "branch_retention": [any(row[2] == branch for row in final_frontier)
                                 for branch in branches]},
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "objectives": list(selected[1]),
            "raw": {"local": list(local), "complete": list(complete)},
            "constraint_graph": graph,
            "bounded_tertiary_frontier": {str(k): v for k, v in relations.items()},
            "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
            "sidechain_graph_spatial_exclusion":
                sidechain_graph_spatial_exclusion_relation(sequence, atoms)},
        "constraint_graph_census": verify_sequence_constraint_graph(sequence),
        "domain_state_count": DOMAIN_STATE_COUNT, "domain_capacity": DOMAIN_CAPACITY,
        "frontier_capacity": FRONTIER_CAPACITY, "segment_residues": SEGMENT_RESIDUES,
        "whole_chain_evaluations": sum(e.evaluations for e in evaluators.values()),
        "whole_chain_cache_hits": sum(e.cache_hits for e in evaluators.values()),
        "runtime_seconds": time.perf_counter() - started,
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "charge_census": CHARGE_CENSUS, "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
        "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
        "atoms": atoms,
    }
