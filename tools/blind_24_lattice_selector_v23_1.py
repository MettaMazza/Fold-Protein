#!/usr/bin/env python3
"""Selector v23.1: V23 global assembly with parent-path continuity.

The sealed V23 development campaign showed that the 76-residue domain scan
retained only one of 75 parent states before bidirectional assembly.  V23.1
adds exactly one relation: the integer count of departures from the registered
sealed V13 parent path.  It enters the same weight-free ordinal balance as the
other sequence-graph relations.  There is no departure limit, penalty weight,
target feedback, or lock: every one of the 576 states remains evaluated and a
candidate may replace every state when the complete relation selects it.
"""
from __future__ import annotations

import time

from tools.backbone_hydrogen_bond_constitution_v1 import backbone_hydrogen_bond_relation
from tools.backbone_hydrogen_bond_constitution_v2 import topology_backbone_hydrogen_bond_relation
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY, HARD_EXCLUSION_STRATA,
    HYDROGEN_BOND_CENSUS, SEGMENT_RESIDUES, SIDECHAIN_GRAPH_SPATIAL_CENSUS,
    TOPOLOGY_HYDROGEN_BOND_CENSUS, _WholeChainEvaluator, _assemble_direction,
    _atoms_for_states, _rich_final_row, _scan_complete_domains, _segments,
    _select_unique)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import (
    sequence_constraint_relations, verify_sequence_constraint_graph)
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


class _ParentContinuousEvaluator(_WholeChainEvaluator):
    def __init__(self, sequence: str, seed: tuple[int, ...]):
        super().__init__(sequence)
        self.seed = seed

    def row(self, states: tuple[int, ...]):
        base = super().row(states)
        departures = sum(left != right for left, right in zip(states, self.seed))
        return (base[0], tuple(base[1]) + (departures,), states)


def _rich_parent_row(sequence: str, states: tuple[int, ...], seed: tuple[int, ...]):
    base, atoms, graph, local, complete = _rich_final_row(sequence, states)
    departures = sum(left != right for left, right in zip(states, seed))
    return ((base[0], tuple(base[1]) + (departures,), states),
            atoms, graph, local, complete, departures)


def select_state_path_v23_1(sequence: str, seed_states) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in seed_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("v23.1 requires a valid registered complete-sequence seed")
    evaluator = _ParentContinuousEvaluator(sequence, seed)
    domains, domain_trace = _scan_complete_domains(sequence, seed, evaluator)
    for index, row in enumerate(domain_trace):
        row["parent_state"] = seed[index]
        row["parent_state_retained"] = seed[index] in row["retained_states"]
    segments = _segments(len(sequence) - 1)
    forward, forward_trace = _assemble_direction(
        seed, domains, segments, evaluator, "forward")
    reverse, reverse_trace = _assemble_direction(
        seed, domains, segments, evaluator, "reverse")
    reconciliation = _select_unique(
        [evaluator.row(path) for path in (*forward, *reverse, seed)],
        FRONTIER_CAPACITY)

    rich_rows = []
    raw = {}
    for _, _, states in reconciliation:
        row, atoms, graph, local, complete, departures = _rich_parent_row(
            sequence, states, seed)
        rich_rows.append(row)
        raw[states] = (atoms, graph, local, complete, departures)
    selected = select_balanced_hierarchy(rich_rows, 1)[0]
    states = selected[2]
    atoms, graph, local, complete, departures = raw[states]
    graph_spatial = sidechain_graph_spatial_exclusion_relation(sequence, atoms)
    return {
        "states": list(states), "seed_states": list(seed),
        "parent_departures": departures,
        "parent_states_retained_in_domains": sum(
            row["parent_state_retained"] for row in domain_trace),
        "domain_trace": domain_trace,
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "unique_input_paths": len({*forward, *reverse, seed}),
            "retained_paths": len(reconciliation),
            "parent_path_retained": any(row[2] == seed for row in reconciliation),
        },
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "objectives": list(selected[1]),
            "parent_departures": departures,
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
