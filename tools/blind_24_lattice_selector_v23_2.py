#!/usr/bin/env python3
"""Selector v23.2: locally closed domains before V23 global assembly.

V23.2 repairs the measured long-chain loss of local geometry by restoring the
ordering already established in V19: all 576 states are evaluated by the V13
local constitution, exactly 24 locally balanced states form each residue
domain, and only those domains enter the unchanged bidirectional whole-chain
segment assembly.  No state is preselected by a target and no score, weight,
reward, fitted parameter, or departure lock is introduced.
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
    TOPOLOGY_HYDROGEN_BOND_CENSUS, _WholeChainEvaluator, _assemble_direction,
    _rich_final_row, _segments, _select_unique)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _scan_locally_closed_domains(sequence: str, seed: tuple[int, ...], evaluator):
    domains = []
    trace = []
    for residue in range(len(sequence) - 1):
        local_rows = []
        global_by_state = {}
        for state in range(DOMAIN_STATE_COUNT):
            candidate = list(seed)
            candidate[residue] = state
            path = tuple(candidate)
            local = generated_local_relations_v19(
                sequence, list(path[:residue + 1]))
            local_rows.append(_local_row(local, (state,)))
            global_by_state[state] = evaluator.row(path)
        locally_held = select_balanced_hierarchy(local_rows, DOMAIN_CAPACITY)
        combined = []
        for _, _, identity in locally_held:
            state = identity[0]
            global_row = global_by_state[state]
            # Local eligibility is the parent stratum; complete-chain relations
            # decide only inside that admitted 24-state domain.
            combined.append((global_row[0], global_row[1], (state,)))
        held = select_balanced_hierarchy(combined, DOMAIN_CAPACITY)
        states = tuple(row[2][0] for row in held)
        if len(states) != DOMAIN_CAPACITY or len(set(states)) != DOMAIN_CAPACITY:
            raise RuntimeError("locally closed residue domain did not retain 24 states")
        domains.append(states)
        trace.append({
            "residue": residue + 1,
            "expanded_state_count": DOMAIN_STATE_COUNT,
            "locally_admitted_state_count": len(locally_held),
            "retained_state_count": len(states),
            "retained_states": list(states),
            "parent_state": seed[residue],
            "parent_state_retained": seed[residue] in states,
            "best_hard_vector": list(held[0][0]),
        })
    return tuple(domains), trace


def select_state_path_v23_2(sequence: str, seed_states) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    seed = tuple(int(state) for state in seed_states)
    if (len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE
            or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed)):
        raise ValueError("v23.2 requires a valid registered complete-sequence seed")
    evaluator = _WholeChainEvaluator(sequence)
    domains, domain_trace = _scan_locally_closed_domains(sequence, seed, evaluator)
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
