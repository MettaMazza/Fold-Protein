#!/usr/bin/env python3
"""Selector v23: complete-domain bidirectional global segment assembly.

V23 is one architectural transition beyond the prefix-greedy selectors:

1. obtain the source-bound V13 complete-sequence path;
2. scan all 576 lattice states at every active residue in whole-chain context;
3. retain a weight-free 24-state domain at each residue;
4. assemble four-residue segments over 24 coordinated alternatives, once from
   each chain direction;
5. reconcile both complete-chain frontiers; and
6. judge the retained alternatives with the explicit V19 atom graph and all
   V13 constitutional relations before emitting one path.

Every finite capacity is counted from the 24-lattice axis, the 576-state
domain, or the already-derived four-residue orientation unit.  No target,
template, fitted parameter, reward, learned quantity, or scalar score weight
enters.
"""
from __future__ import annotations

from collections import OrderedDict
import time

from tools.backbone_hydrogen_bond_constitution_v1 import (
    HYDROGEN_BOND_CENSUS, backbone_hydrogen_bond_relation)
from tools.backbone_hydrogen_bond_constitution_v2 import (
    TOPOLOGY_HYDROGEN_BOND_CENSUS, topology_backbone_hydrogen_bond_relation)
from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE, LATTICE_DEGREES, LATTICE_STATES, angles_for_state,
    validate_sequence)
from tools.blind_24_lattice_selector_v6 import ORIENTATION_MODES, selected_orientation_trace
from tools.blind_24_lattice_selector_v7 import MODE_CAPACITY
from tools.blind_24_lattice_selector_v9 import CHARGE_CENSUS, STERIC_CENSUS
from tools.blind_24_lattice_selector_v19 import (
    _combined_row, _selected_rank_vector, generated_local_relations_v19,
    generated_prefix_relations_v19)
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import (
    SEGMENT_RESIDUES, sequence_constraint_relations,
    verify_sequence_constraint_graph)
from tools.protein_backbone_geometry_v1 import build_backbone_coordinates
from tools.sidechain_graph_spatial_exclusion_v1 import (
    SIDECHAIN_GRAPH_SPATIAL_CENSUS, sidechain_graph_spatial_exclusion_relation)


DOMAIN_STATE_COUNT = len(LATTICE_STATES)
DOMAIN_CAPACITY = len(LATTICE_DEGREES)
FRONTIER_CAPACITY = len(LATTICE_DEGREES)
CACHE_CAPACITY = len(LATTICE_STATES)
HARD_EXCLUSION_STRATA = ("backbone", "sidechain_graph")


def _atoms_for_states(sequence: str, states: tuple[int, ...]):
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    return build_backbone_coordinates(sequence, phi, psi)


class _WholeChainEvaluator:
    """A lattice-counted LRU avoids unbounded whole-chain geometry storage."""

    def __init__(self, sequence: str):
        self.sequence = sequence
        self.cache: OrderedDict[tuple[int, ...], tuple] = OrderedDict()
        self.evaluations = 0
        self.cache_hits = 0

    def row(self, states: tuple[int, ...]):
        held = self.cache.get(states)
        if held is not None:
            self.cache.move_to_end(states)
            self.cache_hits += 1
            return held
        atoms = _atoms_for_states(self.sequence, states)
        graph = sequence_constraint_relations(
            self.sequence, atoms, include_rows=False)
        row = ((int(graph["backbone_exclusions"]),),
               tuple(graph["objectives"] + graph["segment_pair_objectives"]),
               states)
        self.cache[states] = row
        if len(self.cache) > CACHE_CAPACITY:
            self.cache.popitem(last=False)
        self.evaluations += 1
        return row


def _select_unique(rows, width: int):
    unique = {row[2]: row for row in rows}
    return select_balanced_hierarchy(unique.values(), width)


def _scan_complete_domains(sequence: str, seed: tuple[int, ...], evaluator):
    domains = []
    trace = []
    for residue in range(len(sequence) - 1):
        rows = []
        for state in range(DOMAIN_STATE_COUNT):
            candidate = list(seed)
            candidate[residue] = state
            rows.append(evaluator.row(tuple(candidate)))
        selected = _select_unique(rows, DOMAIN_CAPACITY)
        states = tuple(row[2][residue] for row in selected)
        if len(states) != DOMAIN_CAPACITY or len(set(states)) != DOMAIN_CAPACITY:
            raise RuntimeError("complete residue domain did not retain 24 unique states")
        domains.append(states)
        trace.append({
            "residue": residue + 1,
            "expanded_state_count": DOMAIN_STATE_COUNT,
            "retained_state_count": len(states),
            "retained_states": list(states),
            "best_hard_vector": list(selected[0][0]),
        })
    return tuple(domains), trace


def _segments(active_residue_count: int):
    return tuple(tuple(range(start, min(start + SEGMENT_RESIDUES, active_residue_count)))
                 for start in range(0, active_residue_count, SEGMENT_RESIDUES))


def _coordinated_segment_choices(segment, domains):
    choices = []
    for orbit in range(DOMAIN_CAPACITY):
        choices.append(tuple(
            domains[residue][(orbit + offset) % DOMAIN_CAPACITY]
            for offset, residue in enumerate(segment)))
    return tuple(choices)


def _assemble_direction(seed, domains, segments, evaluator, direction):
    frontier = [seed]
    trace = []
    ordered = segments if direction == "forward" else tuple(reversed(segments))
    for segment in ordered:
        rows = []
        choices = _coordinated_segment_choices(segment, domains)
        for path in frontier:
            for choice in choices:
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


def _rich_final_row(sequence: str, states: tuple[int, ...]):
    state_path = list(states[:-1])
    local = generated_local_relations_v19(sequence, state_path)
    complete = generated_prefix_relations_v19(sequence, state_path)
    base = _combined_row(local, complete, states)
    atoms = _atoms_for_states(sequence, states)
    graph = sequence_constraint_relations(sequence, atoms)
    return (tuple(base[0]),
            tuple(base[1]) + tuple(graph["objectives"])
            + tuple(graph["segment_pair_objectives"]),
            states), atoms, graph, local, complete


def select_state_path_v23(sequence: str, seed_states=None) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    if len(sequence) == 1:
        atoms = _atoms_for_states(sequence, (CANONICAL_STATE,))
        graph = sequence_constraint_relations(sequence, atoms)
        return {
            "states": [CANONICAL_STATE], "domain_trace": [],
            "assembly_trace": [], "final_relations": {
                "hard_exclusions": 0, "hard_exclusion_vector": [0, 0],
                "constraint_graph": graph},
            "constraint_graph_census": verify_sequence_constraint_graph(sequence),
            "domain_state_count": DOMAIN_STATE_COUNT,
            "domain_capacity": DOMAIN_CAPACITY,
            "frontier_capacity": FRONTIER_CAPACITY,
            "segment_residues": SEGMENT_RESIDUES,
            "whole_chain_evaluations": 0, "whole_chain_cache_hits": 0,
            "runtime_seconds": time.perf_counter() - started,
            "orientation_modes": ORIENTATION_MODES, "orientation_trace": [],
            "charge_census": CHARGE_CENSUS, "steric_census": STERIC_CENSUS,
            "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
            "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
            "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
            "atoms": atoms,
        }

    if seed_states is None:
        raise ValueError(
            "v23 requires a source-bound complete-sequence seed state path")
    seed = tuple(int(state) for state in seed_states)
    if any(state < 0 or state >= DOMAIN_STATE_COUNT for state in seed):
        raise ValueError("v23 seed contains a state outside the 576-state lattice")
    if len(seed) != len(sequence) or seed[-1] != CANONICAL_STATE:
        raise RuntimeError("V13 source-bound seed boundary did not close")
    evaluator = _WholeChainEvaluator(sequence)
    domains, domain_trace = _scan_complete_domains(sequence, seed, evaluator)
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
    return {
        "states": list(states),
        "seed_states": list(seed),
        "domain_trace": domain_trace,
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "unique_input_paths": len({*forward, *reverse, seed}),
            "retained_paths": len(reconciliation),
        },
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "objectives": list(selected[1]),
            "ordinal_rank_vector": _selected_rank_vector(rich_rows, selected),
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
