#!/usr/bin/env python3
"""Selector V27: constitutional reconciliation of V25 and V26.1.

V25 supplies the strongest full-length topology branch and V26.1 the strongest
full-length distance-geometry branch.  V27 treats their differing states as a
binary fold domain, exhausts every branch combination while that complete cube
fits inside the already derived 576-state lattice domain, and retains 24 paths
through the unchanged rich constitution.  That reconciled frontier then seeds
the V25 one-coordinate basis in both chain directions.

The binary branch choice, 576 complete-domain boundary, 24-state local domains,
24-path frontier, and four-residue units are inherited counted quantities.  No
target, target score, fitted blend, scalar weight, reward, continuity penalty,
template, or learned parameter enters.
"""
from __future__ import annotations

from itertools import product
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
from tools.blind_24_lattice_selector_v25 import _coordinate_candidates
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import verify_sequence_constraint_graph
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation


def _complete_branch_cube(left: tuple[int, ...], right: tuple[int, ...]):
    differences = tuple(
        index for index, (a, b) in enumerate(zip(left, right)) if a != b)
    cube_size = 1 << len(differences)
    if cube_size > DOMAIN_STATE_COUNT:
        raise RuntimeError(
            "V27 complete binary branch cube exceeds the derived 576-state domain")
    candidates = []
    for choices in product((0, 1), repeat=len(differences)):
        candidate = list(left)
        for residue, choice in zip(differences, choices):
            candidate[residue] = right[residue] if choice else left[residue]
        candidates.append(tuple(candidate))
    if len(set(candidates)) != cube_size:
        raise RuntimeError("V27 binary branch cube did not close")
    return tuple(candidates), differences


def _rich_cube_frontier(sequence, candidates):
    rows = []
    for states in candidates:
        row, _, _, _, _ = _rich_final_row(sequence, states)
        rows.append(row)
    return tuple(
        row[2] for row in select_balanced_hierarchy(rows, FRONTIER_CAPACITY))


def _coordinate_beam_from_frontier(frontier, domains, segments, evaluator,
                                   direction):
    frontier = tuple(frontier)
    trace = []
    ordered = segments if direction == "forward" else tuple(reversed(segments))
    for segment in ordered:
        candidates = set()
        for path in frontier:
            candidates.update(_coordinate_candidates(path, segment, domains))
        selected = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in selected)
        trace.append({
            "direction": direction,
            "segment_residues": [residue + 1 for residue in segment],
            "expanded_unique_paths": len(candidates),
            "retained_paths": len(frontier),
            "best_hard_vector": list(selected[0][0]),
        })
    return frontier, trace


def select_state_path_v27(sequence: str, v25_states, v26_1_states,
                          domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    v25 = tuple(int(state) for state in v25_states)
    v261 = tuple(int(state) for state in v26_1_states)
    for name, states in (("V25", v25), ("V26.1", v261)):
        if (len(states) != len(sequence) or states[-1] != CANONICAL_STATE
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise ValueError(f"V27 requires a valid sealed {name} branch")
    domains = _validated_domains(sequence, domain_trace)
    cube, differences = _complete_branch_cube(v25, v261)
    cube_frontier = _rich_cube_frontier(sequence, cube)
    segments = _segments(len(sequence) - 1)
    evaluator = _WholeChainEvaluator(sequence)
    forward, forward_trace = _coordinate_beam_from_frontier(
        cube_frontier, domains, segments, evaluator, "forward")
    reverse, reverse_trace = _coordinate_beam_from_frontier(
        cube_frontier, domains, segments, evaluator, "reverse")

    candidates = {*forward, *reverse, *cube_frontier, v25, v261}
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
        "v25_states": list(v25), "v26_1_states": list(v261),
        "v25_departures": sum(a != b for a, b in zip(states, v25)),
        "v26_1_departures": sum(a != b for a, b in zip(states, v261)),
        "branch_cube": {
            "difference_residues": [index + 1 for index in differences],
            "binary_dimension": len(differences),
            "complete_candidate_count": len(cube),
            "retained_paths": len(cube_frontier),
        },
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "cube_paths": len(cube_frontier),
            "unique_input_paths": len(candidates),
            "retained_paths": len(reconciliation),
            "v25_retained": any(row[2] == v25 for row in reconciliation),
            "v26_1_retained": any(row[2] == v261 for row in reconciliation),
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
