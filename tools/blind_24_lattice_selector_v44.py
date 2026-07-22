#!/usr/bin/env python3
"""V44: connected One-cycle paired-state fixed-point frontier.

V42 supplies the complete three-row connected whole-chain frontier. V43
supplies the exact finite-graph cycle rank and the theorem-forced One. From
every V42 parent, V44 exhausts all 576 paired states at every active residue in
the registered N-to-C direction while preserving connectivity. Each scan
descends the absolute integer distance of the cycle rank to One, with the
already-admitted V3 order acting only inside an identical cycle distance.
Complete sweeps repeat to strict fixed point and every distinct fixed point is
retained. No target, comparison score, mask preference, beam, cutoff, weight,
reward or fitted parameter enters.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

import numpy as np

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    dimensionless_topology_key,
    validate_sequence,
)
from tools.blind_24_lattice_selector_v38 import PAIRED_STATE_COUNT
from tools.blind_24_lattice_selector_v40 import (
    CAUSAL_DIRECTION,
    PARALLEL_WORKERS,
    _replace_paired_state,
)
from tools.blind_24_lattice_selector_v42 import backbone_contact_row
from tools.blind_24_lattice_selector_v43 import graph_cycle_rank


EXPECTED_CONNECTED_PARENTS = 3
EXPECTED_BLOCKS = 26
CYCLE_TARGET = 1


def cycle_distance_to_one(cycle_rank: int) -> int:
    if cycle_rank < 0:
        raise ValueError("cycle rank cannot be negative")
    return abs(cycle_rank - CYCLE_TARGET)


def _connected_cycle_rank(sequence: str, path: tuple[int, ...], blocks):
    detail = backbone_contact_row(sequence, path, blocks)
    if detail["graph_components"] != 1:
        return None
    cycle_rank = graph_cycle_rank(
        detail["interblock_edges"], len(blocks), detail["graph_components"]
    )
    ca = np.asarray(
        [atom["coord"] for atom in detail["atoms"] if atom["name"] == "CA"],
        dtype=float,
    )
    topology = dimensionless_topology_key(sequence, ca)
    rank = (cycle_distance_to_one(cycle_rank), topology, path)
    return rank, {
        "graph_components": detail["graph_components"],
        "graph_cycle_rank": cycle_rank,
        "interblock_edges": detail["interblock_edges"],
        "contact_residue_pairs": detail["contact_residue_pairs"],
        "contact_atom_pairs": detail["contact_atom_pairs"],
    }


def _rank_replacement(task):
    sequence, current, blocks, residue, state = task
    candidate = _replace_paired_state(current, residue, state)
    ranked = _connected_cycle_rank(sequence, candidate, blocks)
    if ranked is None:
        return None
    rank, graph = ranked
    return rank, candidate, graph


def _connected_one_cycle_fixed_point(
    sequence: str,
    seed: tuple[int, ...],
    blocks,
    label: str,
    executor: ProcessPoolExecutor | None = None,
) -> dict:
    initial = _connected_cycle_rank(sequence, seed, blocks)
    if initial is None:
        raise RuntimeError("V44 received a disconnected V42 parent")
    current = seed
    current_rank, current_graph = initial
    sweeps = []
    evaluations = connected_evaluations = 0
    while True:
        sweep_start = current
        changed_states = 0
        for residue in range(len(current)):
            tasks = (
                (sequence, current, blocks, residue, state)
                for state in range(PAIRED_STATE_COUNT)
            )
            if executor is None:
                ranked = list(map(_rank_replacement, tasks))
            else:
                ranked = list(executor.map(
                    _rank_replacement, tasks, chunksize=PARALLEL_WORKERS
                ))
            evaluations += len(ranked)
            connected = [row for row in ranked if row is not None]
            connected_evaluations += len(connected)
            if not connected:
                raise RuntimeError("V44 complete scan lost its connected parent")
            winner_rank, winner, winner_graph = min(
                connected, key=lambda row: row[0]
            )
            if winner_rank > current_rank:
                raise RuntimeError("V44 connected cycle scan violated monotone descent")
            if winner != current:
                changed_states += 1
            current, current_rank, current_graph = (
                winner, winner_rank, winner_graph
            )
        sweeps.append({
            "sweep": len(sweeps) + 1,
            "changed_states": changed_states,
            "cycle_distance_to_one": current_rank[0],
            "graph_cycle_rank": current_graph["graph_cycle_rank"],
            "rank_key": list(current_rank[1]),
        })
        if current == sweep_start:
            break
    if sweeps[-1]["changed_states"] != 0:
        raise RuntimeError("V44 returned before a stable complete sweep")
    return {
        "seed": label,
        "path": list(current),
        "cycle_distance_to_one": current_rank[0],
        "rank_key": list(current_rank[1]),
        **current_graph,
        "sweeps": sweeps,
        "evaluations": evaluations,
        "connected_evaluations": connected_evaluations,
    }


def _blocks_from_record(v42_record: dict):
    blocks = []
    for row in v42_record.get("blocks", []):
        members = tuple(int(residue) - 1 for residue in row["residues"])
        blocks.append((row["status"] == "disagree", members))
    if (len(blocks) != EXPECTED_BLOCKS
            or sorted(member for _, members in blocks for member in members)
            != list(range(len(v42_record["sequence"])))):
        raise RuntimeError("V44 V42 block partition drifted")
    return tuple(blocks)


def select_state_frontier_v44(
    sequence: str, v42_record: dict, parallel: bool = True
) -> dict:
    sequence = validate_sequence(sequence)
    if v42_record.get("schema") != "fold-protein-selected-frontier/v42":
        raise RuntimeError("V44 requires the sealed V42 connected frontier")
    if v42_record.get("sequence") != sequence:
        raise RuntimeError("V44 sequence differs from its V42 parent")
    parents = v42_record.get("frontier", [])
    if (v42_record.get("connected_frontier_count")
            != EXPECTED_CONNECTED_PARENTS or len(parents)
            != EXPECTED_CONNECTED_PARENTS):
        raise RuntimeError("V44 requires all three V42 connected parents")
    blocks = _blocks_from_record(v42_record)
    seeds = []
    for row in parents:
        path = tuple(row["path"])
        if (len(path) != len(sequence) - 1
                or row.get("graph_components") != 1):
            raise RuntimeError("V44 V42 parent identity drifted")
        seeds.append((f'v42_mask_{row["mask"]}', path))
    if len({path for _, path in seeds}) != EXPECTED_CONNECTED_PARENTS:
        raise RuntimeError("V44 connected parent frontier collapsed")

    if (PAIRED_STATE_COUNT != 576 or CAUSAL_DIRECTION != "n_to_c"
            or CYCLE_TARGET != 1):
        raise RuntimeError("V44 counted descent constitution drifted")
    if parallel:
        with ProcessPoolExecutor(
            max_workers=PARALLEL_WORKERS,
            mp_context=get_context("fork"),
        ) as executor:
            traces = [
                _connected_one_cycle_fixed_point(
                    sequence, path, blocks, label, executor=executor
                )
                for label, path in seeds
            ]
    else:
        traces = [
            _connected_one_cycle_fixed_point(sequence, path, blocks, label)
            for label, path in seeds
        ]
    if {row["seed"] for row in traces} != {label for label, _ in seeds}:
        raise RuntimeError("V44 did not execute the complete connected frontier")

    distinct = {}
    for row in traces:
        path = tuple(row["path"])
        distinct.setdefault(path, []).append(row["seed"])
    frontier = []
    for path, seed_labels in sorted(distinct.items()):
        ranked = _connected_cycle_rank(sequence, path, blocks)
        if ranked is None:
            raise RuntimeError("V44 fixed point lost connectedness")
        rank, graph = ranked
        frontier.append({
            "states": list(path) + [CANONICAL_STATE],
            "source_seeds": seed_labels,
            "cycle_distance_to_one": rank[0],
            "rank_key": list(rank[1]),
            **graph,
        })
    return {
        "connected_parent_count": len(seeds),
        "paired_state_count": PAIRED_STATE_COUNT,
        "causal_direction": CAUSAL_DIRECTION,
        "cycle_rank_target": CYCLE_TARGET,
        "block_count": len(blocks),
        "fixed_point_trace": traces,
        "distinct_fixed_points": len(frontier),
        "frontier": frontier,
        "total_evaluations": sum(row["evaluations"] for row in traces),
        "total_connected_evaluations": sum(
            row["connected_evaluations"] for row in traces
        ),
        "parallel_workers": PARALLEL_WORKERS if parallel else 0,
    }
