#!/usr/bin/env python3
"""Selector V28: multiscale constitutional branch propagation.

V27 established that complete residue-wise reconciliation advances the short
and intermediate branches but does not carry the strongest V25/V26.1 relation
through all 76 residues.  V28 therefore changes assembly scale.  Starting
from the sealed V25, V26.1 and V27 paths, it partitions the active chain into
four-residue blocks and repeatedly doubles the block span until one block
contains the chain.  At every scale and in both directions, every retained
path exposes (a) the unchanged path, (b) the complete block from each sealed
branch, and (c) every locally admitted one-coordinate transition at both
block boundaries.  The same whole-chain constitution retains 24 paths after
each block and reconciles both directions after each scale.

Four residues, binary boundaries, repeated doubling, three sealed branches,
24-state local domains and a 24-path frontier are counted inherited
quantities.  No target, score, fitted blend, scalar weight, reward, template,
continuity lock or learned parameter enters selection.
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
    _WholeChainEvaluator, _rich_final_row, _select_unique)
from tools.blind_24_lattice_selector_v24 import _validated_domains
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _scales(active_length: int) -> tuple[int, ...]:
    scales, span = [], SEGMENT_RESIDUES
    while True:
        scales.append(span)
        if span >= active_length:
            return tuple(scales)
        span *= 2


def _blocks(active_length: int, span: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(range(start, min(start + span, active_length)))
        for start in range(0, active_length, span))


def _block_candidates(path, block, branches, domains):
    candidates = {path}
    for branch in branches:
        graft = list(path)
        for residue in block:
            graft[residue] = branch[residue]
        candidates.add(tuple(graft))
    boundaries = (block[0],) if len(block) == 1 else (block[0], block[-1])
    for residue in boundaries:
        for state in domains[residue]:
            candidate = list(path)
            candidate[residue] = state
            candidates.add(tuple(candidate))
    return candidates


def _directional_scale(frontier, blocks, branches, domains, evaluator,
                       scale, direction):
    trace = []
    ordered = blocks if direction == "forward" else tuple(reversed(blocks))
    for block in ordered:
        candidates = set(branches)
        for path in frontier:
            candidates.update(_block_candidates(path, block, branches, domains))
        selected = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in selected)
        trace.append({
            "scale_residues": scale,
            "direction": direction,
            "block_residues": [residue + 1 for residue in block],
            "boundary_residues": [block[0] + 1, block[-1] + 1],
            "expanded_unique_paths": len(candidates),
            "retained_paths": len(frontier),
            "branch_retention": [branch in frontier for branch in branches],
            "best_hard_vector": list(selected[0][0]),
        })
    return frontier, trace


def select_state_path_v28(sequence: str, v25_states, v26_1_states,
                          v27_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    branches = tuple(tuple(int(state) for state in states) for states in (
        v25_states, v26_1_states, v27_states))
    for name, states in zip(("V25", "V26.1", "V27"), branches):
        if (len(states) != len(sequence) or states[-1] != CANONICAL_STATE
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise ValueError(f"V28 requires a valid sealed {name} branch")
    domains = _validated_domains(sequence, domain_trace)
    evaluator = _WholeChainEvaluator(sequence)
    active_length = len(sequence) - 1
    frontier = tuple(dict.fromkeys(branches))
    scale_trace = []

    for scale in _scales(active_length):
        blocks = _blocks(active_length, scale)
        forward, forward_trace = _directional_scale(
            frontier, blocks, branches, domains, evaluator, scale, "forward")
        reverse, reverse_trace = _directional_scale(
            frontier, blocks, branches, domains, evaluator, scale, "reverse")
        candidates = {*forward, *reverse, *frontier, *branches}
        reconciled = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in reconciled)
        scale_trace.append({
            "scale_residues": scale,
            "block_count": len(blocks),
            "forward": forward_trace,
            "reverse": reverse_trace,
            "reconciliation_candidates": len(candidates),
            "retained_paths": len(frontier),
            "branch_retention": [branch in frontier for branch in branches],
        })

    candidates = {*frontier, *branches}
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
    return {
        "states": list(states),
        "v25_states": list(branches[0]),
        "v26_1_states": list(branches[1]),
        "v27_states": list(branches[2]),
        "v25_departures": sum(a != b for a, b in zip(states, branches[0])),
        "v26_1_departures": sum(a != b for a, b in zip(states, branches[1])),
        "v27_departures": sum(a != b for a, b in zip(states, branches[2])),
        "scales": list(_scales(active_length)),
        "scale_trace": scale_trace,
        "reconciliation": {
            "unique_input_paths": len(candidates),
            "retained_paths": len(reconciliation),
            "branch_retention": [
                any(row[2] == branch for row in reconciliation)
                for branch in branches],
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
        "whole_chain_evaluations": evaluator.evaluations,
        "whole_chain_cache_hits": evaluator.cache_hits,
        "runtime_seconds": time.perf_counter() - started,
        "orientation_modes": ORIENTATION_MODES,
        "orientation_trace": selected_orientation_trace(sequence, states),
        "charge_census": CHARGE_CENSUS,
        "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
        "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
        "atoms": atoms,
    }
