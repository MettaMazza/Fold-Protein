#!/usr/bin/env python3
"""Selector V30: degree-two tertiary segment-path assembly."""
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
from tools.tertiary_segment_body_constitution_v2 import (
    build_tertiary_segment_path, tertiary_segment_path_relation,
    verify_tertiary_segment_path_constitution)


class _PathEvaluator:
    def __init__(self, sequence):
        self.sequence, self.cache = sequence, OrderedDict()
        self.evaluations = self.cache_hits = 0

    def row(self, states):
        held = self.cache.get(states)
        if held is not None:
            self.cache.move_to_end(states)
            self.cache_hits += 1
            return held
        atoms = _atoms_for_states(self.sequence, states)
        graph = sequence_constraint_relations(self.sequence, atoms, include_rows=False)
        path = tertiary_segment_path_relation(self.sequence, atoms)
        row = ((int(graph["backbone_exclusions"]),),
               tuple(path["objectives"] + graph["objectives"]
                     + graph["segment_pair_objectives"]), states)
        self.cache[states] = row
        if len(self.cache) > CACHE_CAPACITY:
            self.cache.popitem(last=False)
        self.evaluations += 1
        return row


def select_state_path_v30(sequence: str, v25_states, v26_1_states,
                          v27_states, v28_states, domain_trace) -> dict:
    sequence, started = validate_sequence(sequence), time.perf_counter()
    branches = tuple(tuple(int(state) for state in states) for states in (
        v25_states, v26_1_states, v27_states, v28_states))
    for name, states in zip(("V25", "V26.1", "V27", "V28"), branches):
        if (len(states) != len(sequence) or states[-1] != CANONICAL_STATE
                or any(state < 0 or state >= DOMAIN_STATE_COUNT for state in states)):
            raise ValueError(f"V30 requires a valid sealed {name} branch")
    domains = _validated_domains(sequence, domain_trace)
    topology = build_tertiary_segment_path(sequence)
    evaluator = _PathEvaluator(sequence)
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
        tertiary = tertiary_segment_path_relation(sequence, atoms)
        row = (base[0], tuple(tertiary["objectives"]) + base[1], states)
        rich_rows.append(row)
        raw[states] = (atoms, graph, local, complete, tertiary)
    selected = select_balanced_hierarchy(rich_rows, 1)[0]
    states = selected[2]
    atoms, graph, local, complete, tertiary = raw[states]
    return {
        "states": list(states),
        "v25_states": list(branches[0]), "v26_1_states": list(branches[1]),
        "v27_states": list(branches[2]), "v28_states": list(branches[3]),
        **{name + "_departures": sum(a != b for a, b in zip(states, branch))
           for name, branch in zip(("v25", "v26_1", "v27", "v28"), branches)},
        "tertiary_topology": list(topology),
        "tertiary_census": verify_tertiary_segment_path_constitution(sequence),
        "assembly_trace": forward_trace + reverse_trace,
        "reconciliation": {
            "forward_paths": len(forward), "reverse_paths": len(reverse),
            "unique_input_paths": len(candidates),
            "retained_paths": len(reconciliation),
            "branch_retention": [any(row[2] == branch for row in reconciliation)
                                 for branch in branches]},
        "final_relations": {
            "hard_exclusions": sum(selected[0]),
            "hard_exclusion_vector": list(selected[0]),
            "hard_exclusion_strata": list(HARD_EXCLUSION_STRATA),
            "objectives": list(selected[1]),
            "raw": {"local": list(local), "complete": list(complete)},
            "constraint_graph": graph, "tertiary_segment_path": tertiary,
            "hydrogen_bond_assembly": backbone_hydrogen_bond_relation(sequence, atoms),
            "hydrogen_bond_topologies": topology_backbone_hydrogen_bond_relation(sequence, atoms),
            "sidechain_graph_spatial_exclusion":
                sidechain_graph_spatial_exclusion_relation(sequence, atoms)},
        "constraint_graph_census": verify_sequence_constraint_graph(sequence),
        "domain_state_count": DOMAIN_STATE_COUNT, "domain_capacity": DOMAIN_CAPACITY,
        "frontier_capacity": FRONTIER_CAPACITY, "segment_residues": SEGMENT_RESIDUES,
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
