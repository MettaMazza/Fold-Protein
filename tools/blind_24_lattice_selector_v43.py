#!/usr/bin/env python3
"""V43: complete One-cycle frontier over the sealed V42 component cube.

For a finite undirected graph, the exact independent-cycle count is
E - V + C. V42 already seals E, V and C for every one of its 8,192 target-free
block graphs. V43 retains every row whose cycle count is the theorem-forced One.
No target, measured score, mask choice or inherited candidate order enters.
"""
from __future__ import annotations

from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence


EXPECTED_BLOCKS = 26
EXPECTED_CUBE_CANDIDATES = 8192


def graph_cycle_rank(interblock_edges: int, block_count: int,
                     graph_components: int) -> int:
    rank = interblock_edges - block_count + graph_components
    if rank < 0:
        raise RuntimeError("V43 finite graph has a negative cycle rank")
    return rank


def select_state_frontier_v43(sequence: str, v42_record: dict) -> dict:
    sequence = validate_sequence(sequence)
    if v42_record.get("schema") != "fold-protein-selected-frontier/v42":
        raise RuntimeError("V43 requires the sealed V42 complete cube")
    if v42_record.get("sequence") != sequence:
        raise RuntimeError("V43 sequence differs from its sealed V42 parent")
    if (v42_record.get("block_count") != EXPECTED_BLOCKS
            or v42_record.get("component_cube_candidates")
            != EXPECTED_CUBE_CANDIDATES):
        raise RuntimeError("V43 parent graph census drifted")
    trace = v42_record.get("component_cube_trace", [])
    if (len(trace) != EXPECTED_CUBE_CANDIDATES
            or [row.get("mask") for row in trace]
            != list(range(EXPECTED_CUBE_CANDIDATES))):
        raise RuntimeError("V43 parent cube is incomplete or unordered")

    frontier = []
    cycle_census = {}
    for row in trace:
        cycle_rank = graph_cycle_rank(
            row["interblock_edges"], EXPECTED_BLOCKS, row["graph_components"]
        )
        cycle_census[cycle_rank] = cycle_census.get(cycle_rank, 0) + 1
        if cycle_rank == 1:
            states = list(row["path"]) + [CANONICAL_STATE]
            if len(states) != len(sequence):
                raise RuntimeError("V43 retained path length drifted")
            frontier.append({
                "mask": row["mask"],
                "states": states,
                "graph_cycle_rank": cycle_rank,
                "graph_components": row["graph_components"],
                "interblock_edges": row["interblock_edges"],
                "contact_residue_pairs": row["contact_residue_pairs"],
                "contact_atom_pairs": row["contact_atom_pairs"],
            })
    if not frontier:
        raise RuntimeError("V43 complete cube contains no One-cycle graph")
    if any(row["graph_cycle_rank"] != 1 for row in frontier):
        raise RuntimeError("V43 retained a graph outside the One-cycle frontier")
    return {
        "block_count": EXPECTED_BLOCKS,
        "component_cube_candidates": len(trace),
        "cycle_rank_target": 1,
        "cycle_rank_census": {
            str(rank): count for rank, count in sorted(cycle_census.items())
        },
        "one_cycle_frontier_count": len(frontier),
        "frontier": frontier,
    }
