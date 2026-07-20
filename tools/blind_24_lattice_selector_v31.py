#!/usr/bin/env python3
"""Selector V31: retained bounded-degree tertiary topology frontier."""
from __future__ import annotations

from collections import OrderedDict
import time

from tools.backbone_hydrogen_bond_constitution_v1 import backbone_hydrogen_bond_relation
from tools.backbone_hydrogen_bond_constitution_v2 import topology_backbone_hydrogen_bond_relation
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v23 import (
    CACHE_CAPACITY, DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY,
    HARD_EXCLUSION_STRATA, HYDROGEN_BOND_CENSUS, SEGMENT_RESIDUES,
    SIDECHAIN_GRAPH_SPATIAL_CENSUS, TOPOLOGY_HYDROGEN_BOND_CENSUS,
    _atoms_for_states, _rich_final_row, _select_unique)
from tools.blind_24_lattice_selector_v24 import _validated_domains
from tools.blind_24_lattice_selector_v29 import _assemble_edges
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import (
    sequence_constraint_relations, verify_sequence_constraint_graph)
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation
from tools.tertiary_segment_body_constitution_v3 import (
    DEGREE_FRONTIER, bounded_tertiary_relation, build_bounded_tertiary_topology,
    verify_tertiary_topology_frontier)


class _BoundedTopologyEvaluator:
    def __init__(self, sequence, degree_capacity):
        self.sequence, self.degree_capacity = sequence, degree_capacity
        self.cache, self.evaluations, self.cache_hits = OrderedDict(), 0, 0

    def row(self, states):
        held = self.cache.get(states)
        if held is not None:
            self.cache.move_to_end(states)
            self.cache_hits += 1
            return held
        atoms = _atoms_for_states(self.sequence, states)
        graph = sequence_constraint_relations(self.sequence, atoms, include_rows=False)
        relation = bounded_tertiary_relation(
            self.sequence, atoms, self.degree_capacity)
        row = ((int(graph["backbone_exclusions"]),),
               tuple(relation["objectives"] + graph["objectives"]
                     + graph["segment_pair_objectives"]), states)
        self.cache[states] = row
        if len(self.cache) > CACHE_CAPACITY:
            self.cache.popitem(last=False)
        self.evaluations += 1
        return row


def select_state_path_v31(sequence: str, v25_states, v26_1_states,
                          v27_states, v28_states, v29_states, v30_states,
                          domain_trace) -> dict:
    sequence, started = validate_sequence(sequence), time.perf_counter()
    names = ("v25", "v26_1", "v27", "v28", "v29", "v30")
    branches = tuple(tuple(int(state) for state in states) for states in (
        v25_states, v26_1_states, v27_states, v28_states, v29_states, v30_states))
    for name, states in zip(names, branches):
        if (len(states) != len(sequence) or states[-1] != CANONICAL_STATE
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise ValueError(f"V31 requires a valid sealed {name.upper()} branch")
    domains = _validated_domains(sequence, domain_trace)
    seed = tuple(dict.fromkeys(branches))
    topology_traces, topology_frontiers, evaluators = [], {}, {}
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
        retained = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in retained)
        topology_frontiers[capacity] = frontier
        all_candidates.update(frontier)
        topology_traces.append({
            "degree_capacity": capacity,
            "topology": list(topology),
            "forward_trace": forward_trace, "reverse_trace": reverse_trace,
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "reconciliation_inputs": len(candidates),
            "retained_paths": len(frontier),
            "branch_retention": [branch in frontier for branch in branches],
        })

    rich_rows, raw = [], {}
    for states in sorted(all_candidates):
        base, atoms, graph, local, complete = _rich_final_row(sequence, states)
        relations = {
            capacity: bounded_tertiary_relation(sequence, atoms, capacity)
            for capacity in DEGREE_FRONTIER}
        frontier_objectives = [objective for capacity in DEGREE_FRONTIER
                               for objective in relations[capacity]["objectives"]]
        row = (base[0], tuple(frontier_objectives) + base[1], states)
        rich_rows.append(row)
        raw[states] = (atoms, graph, local, complete, relations)
    final_frontier = select_balanced_hierarchy(rich_rows, FRONTIER_CAPACITY)
    selected = final_frontier[0]
    states = selected[2]
    atoms, graph, local, complete, relations = raw[states]
    return {
        "states": list(states),
        **{name + "_states": list(branch) for name, branch in zip(names, branches)},
        **{name + "_departures": sum(a != b for a, b in zip(states, branch))
           for name, branch in zip(names, branches)},
        "tertiary_census": verify_tertiary_topology_frontier(sequence),
        "topology_traces": topology_traces,
        "reconciliation": {
            "unique_input_paths": len(all_candidates),
            "retained_paths": len(final_frontier),
            "branch_retention": [any(row[2] == branch for row in final_frontier)
                                 for branch in branches],
            "topology_frontier_retention": {
                str(capacity): sum(row[2] in topology_frontiers[capacity]
                                   for row in final_frontier)
                for capacity in DEGREE_FRONTIER}},
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
