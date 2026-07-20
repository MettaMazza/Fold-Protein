#!/usr/bin/env python3
"""Selector V29: joint tertiary segment-body topology assembly.

V29 changes the represented object from residue or scale frontiers to a
sequence-forced contact tree of four-residue bodies.  Each tree edge jointly
exposes all complete parent-body graft combinations, every admitted state at
the two boundaries of both bodies, and 24 coordinated paired-boundary moves.
The tertiary tree relation judges those candidates together with the existing
whole-chain constitution in both edge directions.

The topology is fixed from sequence before coordinates. Four-residue bodies,
two boundaries, four sealed parent branches, 24-state domains and the 24-path
frontier are counted inherited quantities. No target, template, fitted
cutoff, scalar weight, reward, lock or learned parameter enters.
"""
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
from tools.constitutional_lexicographic_exclusion_v1 import select_balanced_hierarchy
from tools.global_sequence_constraint_graph_v1 import (
    sequence_constraint_relations, verify_sequence_constraint_graph)
from tools.sidechain_graph_spatial_exclusion_v1 import sidechain_graph_spatial_exclusion_relation
from tools.tertiary_segment_body_constitution_v1 import (
    build_tertiary_segment_topology, tertiary_segment_body_relation,
    verify_tertiary_segment_body_constitution)


class _TertiaryEvaluator:
    def __init__(self, sequence):
        self.sequence = sequence
        self.cache = OrderedDict()
        self.evaluations = 0
        self.cache_hits = 0

    def row(self, states):
        held = self.cache.get(states)
        if held is not None:
            self.cache.move_to_end(states)
            self.cache_hits += 1
            return held
        atoms = _atoms_for_states(self.sequence, states)
        graph = sequence_constraint_relations(self.sequence, atoms, include_rows=False)
        tertiary = tertiary_segment_body_relation(self.sequence, atoms)
        row = (
            (int(graph["backbone_exclusions"]),),
            tuple(tertiary["objectives"] + graph["objectives"]
                  + graph["segment_pair_objectives"]),
            states,
        )
        self.cache[states] = row
        if len(self.cache) > CACHE_CAPACITY:
            self.cache.popitem(last=False)
        self.evaluations += 1
        return row


def _edge_blocks(topology_edge):
    return (tuple(residue - 1 for residue in topology_edge["left_residues"]),
            tuple(residue - 1 for residue in topology_edge["right_residues"]))


def _edge_candidates(path, left, right, branches, domains):
    candidates = {path}
    # Complete body inheritance from every ordered parent pair.
    for left_source in branches:
        for right_source in branches:
            candidate = list(path)
            for residue in left:
                candidate[residue] = left_source[residue]
            for residue in right:
                candidate[residue] = right_source[residue]
            candidates.add(tuple(candidate))
    left_boundaries = tuple(
        residue for residue in ((left[0],) if len(left) == 1 else (left[0], left[-1]))
        if residue < len(domains))
    right_boundaries = tuple(
        residue for residue in ((right[0],) if len(right) == 1 else (right[0], right[-1]))
        if residue < len(domains))
    for residue in tuple(dict.fromkeys(left_boundaries + right_boundaries)):
        for state in domains[residue]:
            candidate = list(path)
            candidate[residue] = state
            candidates.add(tuple(candidate))
    # Coordinate the complete 24-state boundary axis by the counted sequence
    # separation; this is the body-pair move rather than two independent edits.
    for left_residue in left_boundaries:
        for right_residue in right_boundaries:
            offset = abs(right_residue - left_residue) % DOMAIN_CAPACITY
            for orbit in range(DOMAIN_CAPACITY):
                candidate = list(path)
                candidate[left_residue] = domains[left_residue][orbit]
                candidate[right_residue] = domains[right_residue][
                    (orbit + offset) % DOMAIN_CAPACITY]
                candidates.add(tuple(candidate))
    return candidates


def _assemble_edges(frontier, topology, branches, domains, evaluator, direction):
    trace = []
    ordered = topology if direction == "forward" else tuple(reversed(topology))
    for edge_index, edge in enumerate(ordered):
        left, right = _edge_blocks(edge)
        candidates = set(branches)
        for path in frontier:
            candidates.update(_edge_candidates(
                path, left, right, branches, domains))
        selected = _select_unique(
            [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
        frontier = tuple(row[2] for row in selected)
        trace.append({
            "direction": direction,
            "edge_index": edge_index,
            "segments": edge["segments"],
            "left_residues": edge["left_residues"],
            "right_residues": edge["right_residues"],
            "expanded_unique_paths": len(candidates),
            "retained_paths": len(frontier),
            "branch_retention": [branch in frontier for branch in branches],
            "best_hard_vector": list(selected[0][0]),
        })
    return frontier, trace


def select_state_path_v29(sequence: str, v25_states, v26_1_states,
                          v27_states, v28_states, domain_trace) -> dict:
    sequence = validate_sequence(sequence)
    started = time.perf_counter()
    branches = tuple(tuple(int(state) for state in states) for states in (
        v25_states, v26_1_states, v27_states, v28_states))
    for name, states in zip(("V25", "V26.1", "V27", "V28"), branches):
        if (len(states) != len(sequence) or states[-1] != CANONICAL_STATE
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise ValueError(f"V29 requires a valid sealed {name} branch")
    domains = _validated_domains(sequence, domain_trace)
    topology = build_tertiary_segment_topology(sequence)
    evaluator = _TertiaryEvaluator(sequence)
    seed = tuple(dict.fromkeys(branches))
    forward, forward_trace = _assemble_edges(
        seed, topology, branches, domains, evaluator, "forward")
    reverse, reverse_trace = _assemble_edges(
        seed, topology, branches, domains, evaluator, "reverse")

    candidates = {*forward, *reverse, *branches}
    reconciliation = _select_unique(
        [evaluator.row(path) for path in sorted(candidates)], FRONTIER_CAPACITY)
    rich_rows, raw = [], {}
    for _, _, states in reconciliation:
        base, atoms, graph, local, complete = _rich_final_row(sequence, states)
        tertiary = tertiary_segment_body_relation(sequence, atoms)
        row = (base[0], tuple(tertiary["objectives"]) + base[1], states)
        rich_rows.append(row)
        raw[states] = (atoms, graph, local, complete, tertiary)
    selected = select_balanced_hierarchy(rich_rows, 1)[0]
    states = selected[2]
    atoms, graph, local, complete, tertiary = raw[states]
    graph_spatial = sidechain_graph_spatial_exclusion_relation(sequence, atoms)
    return {
        "states": list(states),
        "v25_states": list(branches[0]), "v26_1_states": list(branches[1]),
        "v27_states": list(branches[2]), "v28_states": list(branches[3]),
        "v25_departures": sum(a != b for a, b in zip(states, branches[0])),
        "v26_1_departures": sum(a != b for a, b in zip(states, branches[1])),
        "v27_departures": sum(a != b for a, b in zip(states, branches[2])),
        "v28_departures": sum(a != b for a, b in zip(states, branches[3])),
        "tertiary_topology": list(topology),
        "tertiary_census": verify_tertiary_segment_body_constitution(sequence),
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
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
            "tertiary_segment_bodies": tertiary,
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
        "charge_census": CHARGE_CENSUS, "steric_census": STERIC_CENSUS,
        "hydrogen_bond_census": HYDROGEN_BOND_CENSUS,
        "topology_hydrogen_bond_census": TOPOLOGY_HYDROGEN_BOND_CENSUS,
        "sidechain_graph_spatial_census": SIDECHAIN_GRAPH_SPATIAL_CENSUS,
        "atoms": atoms,
    }
