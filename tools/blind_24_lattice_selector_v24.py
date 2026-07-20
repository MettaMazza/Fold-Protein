#!/usr/bin/env python3
"""Selector v24: coherent local segment frontiers for global assembly.

V24 consumes the complete, sealed V23.2 residue domains and turns each
theorem-counted four-residue segment into 24 locally coherent state tuples.
The tuples are built one residue at a time through the unchanged V19-wrapped
V13 local constitution.  Complete tuples—not independently aligned residue
ranks—then enter V23's forward and reverse whole-chain assembly.

The 576-state census, 24-state domain, 24-path frontier and four-residue
segment are inherited counted quantities.  No target, template, fitted value,
reward, score weight, learned parameter or continuity lock enters.
"""
from __future__ import annotations

import time

from tools.backbone_hydrogen_bond_constitution_v1 import backbone_hydrogen_bond_relation
from tools.backbone_hydrogen_bond_constitution_v2 import topology_backbone_hydrogen_bond_relation
from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v19 import _local_row, generated_local_relations_v19
from tools.blind_24_lattice_selector_v23 import (
    DOMAIN_CAPACITY, DOMAIN_STATE_COUNT, FRONTIER_CAPACITY, HARD_EXCLUSION_STRATA,
    HYDROGEN_BOND_CENSUS, SEGMENT_RESIDUES, SIDECHAIN_GRAPH_SPATIAL_CENSUS,
    TOPOLOGY_HYDROGEN_BOND_CENSUS, _WholeChainEvaluator, _rich_final_row,
    _segments, _select_unique)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _validated_domains(sequence: str, domain_trace) -> tuple[tuple[int, ...], ...]:
    rows = list(domain_trace)
    if len(rows) != len(sequence) - 1:
        raise ValueError("V24 requires one sealed V23.2 domain per active residue")
    domains = []
    for residue, row in enumerate(rows):
        states = tuple(int(state) for state in row.get("retained_states", ()))
        if (row.get("residue") != residue + 1
                or row.get("expanded_state_count") != DOMAIN_STATE_COUNT
                or len(states) != DOMAIN_CAPACITY
                or len(set(states)) != DOMAIN_CAPACITY
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise RuntimeError("sealed V23.2 residue domain did not close")
        domains.append(states)
    return tuple(domains)


def _coherent_segment_frontier(sequence: str, seed: tuple[int, ...],
                               domains, segment: tuple[int, ...]):
    frontier = [tuple(seed[residue] for residue in segment)]
    trace = []
    for offset, residue in enumerate(segment):
        rows = []
        for held in frontier:
            for state in domains[residue]:
                choice = list(held)
                choice[offset] = state
                candidate = list(seed)
                for local_offset in range(offset + 1):
                    candidate[segment[local_offset]] = choice[local_offset]
                local = generated_local_relations_v19(
                    sequence, candidate[:residue + 1])
                rows.append(_local_row(local, tuple(choice)))
        selected = select_balanced_hierarchy(rows, FRONTIER_CAPACITY)
        frontier = [row[2] for row in selected]
        trace.append({
            "residue": residue + 1,
            "expanded_unique_tuples": len({row[2] for row in rows}),
            "retained_tuples": len(frontier),
        })
    if len(frontier) != FRONTIER_CAPACITY or len(set(frontier)) != FRONTIER_CAPACITY:
        raise RuntimeError("coherent segment frontier did not close at 24 tuples")
    return tuple(frontier), trace


def _assemble_coherent_direction(seed, segments, alternatives, evaluator, direction):
    frontier = [seed]
    trace = []
    ordered = segments if direction == "forward" else tuple(reversed(segments))
    for segment in ordered:
        rows = []
        for path in frontier:
            for choice in alternatives[segment]:
                candidate = list(path)
                for residue, state in zip(segment, choice):
                    candidate[residue] = state
                rows.append(evaluator.row(tuple(candidate)))
        selected = _select_unique(rows, FRONTIER_CAPACITY)
        frontier = [row[2] for row in selected]
        trace.append({
            "direction": direction,
            "segment_residues": [residue + 1 for residue in segment],
            "expanded_unique_paths": len({row[2] for row in rows}),
            "retained_paths": len(frontier),
            "best_hard_vector": list(selected[0][0]),
        })
    return tuple(frontier), trace


def select_state_path_v24(sequence: str, seed_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in seed_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("V24 requires a valid registered complete-sequence seed")
    domains = _validated_domains(sequence, domain_trace)
    segments = _segments(len(sequence) - 1)
    alternatives = {}
    segment_generation_trace = []
    for segment in segments:
        held, trace = _coherent_segment_frontier(sequence, seed, domains, segment)
        alternatives[segment] = held
        segment_generation_trace.append({
            "segment_residues": [residue + 1 for residue in segment],
            "domain_cartesian_size": DOMAIN_CAPACITY ** len(segment),
            "retained_tuple_count": len(held),
            "construction_trace": trace,
        })

    evaluator = _WholeChainEvaluator(sequence)
    forward, forward_trace = _assemble_coherent_direction(
        seed, segments, alternatives, evaluator, "forward")
    reverse, reverse_trace = _assemble_coherent_direction(
        seed, segments, alternatives, evaluator, "reverse")
    reconciliation = _select_unique(
        [evaluator.row(path) for path in (*forward, *reverse, seed)],
        FRONTIER_CAPACITY)
    rich_rows = []
    raw = {}
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
        "segment_generation_trace": segment_generation_trace,
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
