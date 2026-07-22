#!/usr/bin/env python3
"""V45: complete boundary-axis connected cycle-to-One fixed-point frontier.

V44 established exact connected One-cycle whole-chain fixed points by complete
paired-state descent.  V38 independently admits the complete coordinate-order
grammar: both chain boundaries crossed with both orders of the two dihedral
axes.  V45 composes those admitted relations.  From every sealed V42 connected
parent it executes all four V38 orders, exhausts all 24 values whenever one
coordinate is active, preserves connectivity, descends exact cycle distance to
the theorem-forced One, and retains every distinct fixed point.  No target,
comparison score, mask preference, beam, cutoff, weight, reward or fitted
parameter enters.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

from tools.blind_24_lattice_selector_v3 import CANONICAL_STATE, validate_sequence
from tools.blind_24_lattice_selector_v38 import (
    AXIS_VALUE_COUNT,
    DESCENT_ORDERS,
    _replace_coordinate,
)
from tools.blind_24_lattice_selector_v40 import PARALLEL_WORKERS
from tools.blind_24_lattice_selector_v44 import (
    CYCLE_TARGET,
    EXPECTED_CONNECTED_PARENTS,
    _blocks_from_record,
    _connected_cycle_rank,
)


EXPECTED_DESCENT_ORDERS = 4
EXPECTED_FIXED_POINT_TRACES = (
    EXPECTED_CONNECTED_PARENTS * EXPECTED_DESCENT_ORDERS
)


def _rank_coordinate_replacement(task):
    sequence, current, blocks, residue, axis, value = task
    candidate = list(current)
    candidate[residue] = _replace_coordinate(
        candidate[residue], axis, value
    )
    candidate_path = tuple(candidate)
    ranked = _connected_cycle_rank(sequence, candidate_path, blocks)
    if ranked is None:
        return None
    rank, graph = ranked
    return rank, candidate_path, graph


def _connected_coordinate_fixed_point(
    sequence: str,
    seed: tuple[int, ...],
    blocks,
    label: str,
    direction: str,
    axis_order: tuple[int, int],
    executor: ProcessPoolExecutor | None = None,
) -> dict:
    initial = _connected_cycle_rank(sequence, seed, blocks)
    if initial is None:
        raise RuntimeError("V45 received a disconnected V42 parent")
    if (direction, axis_order) not in DESCENT_ORDERS:
        raise RuntimeError("V45 received an unregistered boundary-axis order")
    residues = (
        tuple(range(len(seed)))
        if direction == "n_to_c"
        else tuple(reversed(range(len(seed))))
    )
    current = seed
    current_rank, current_graph = initial
    sweeps = []
    evaluations = connected_evaluations = 0
    while True:
        sweep_start = current
        changed_coordinates = 0
        for residue in residues:
            for axis in axis_order:
                tasks = (
                    (sequence, current, blocks, residue, axis, value)
                    for value in range(AXIS_VALUE_COUNT)
                )
                if executor is None:
                    ranked = list(map(_rank_coordinate_replacement, tasks))
                else:
                    ranked = list(executor.map(
                        _rank_coordinate_replacement,
                        tasks,
                        # One complete coordinate scan contains exactly one
                        # task per lattice value.  Unit chunks distribute that
                        # complete 24-value census across all 24 workers;
                        # scheduling cannot alter the independently ranked
                        # candidate rows or their deterministic minimum.
                        chunksize=1,
                    ))
                evaluations += len(ranked)
                connected = [row for row in ranked if row is not None]
                connected_evaluations += len(connected)
                if not connected:
                    raise RuntimeError(
                        "V45 complete coordinate scan lost its connected parent"
                    )
                winner_rank, winner, winner_graph = min(
                    connected, key=lambda row: row[0]
                )
                if winner_rank > current_rank:
                    raise RuntimeError(
                        "V45 connected coordinate scan violated monotone descent"
                    )
                if winner != current:
                    changed_coordinates += 1
                current, current_rank, current_graph = (
                    winner,
                    winner_rank,
                    winner_graph,
                )
        sweeps.append({
            "sweep": len(sweeps) + 1,
            "changed_coordinates": changed_coordinates,
            "cycle_distance_to_one": current_rank[0],
            "graph_cycle_rank": current_graph["graph_cycle_rank"],
            "rank_key": list(current_rank[1]),
        })
        if current == sweep_start:
            break
    if sweeps[-1]["changed_coordinates"] != 0:
        raise RuntimeError("V45 returned before a stable complete sweep")
    return {
        "seed": label,
        "direction": direction,
        "axis_order": list(axis_order),
        "path": list(current),
        "cycle_distance_to_one": current_rank[0],
        "rank_key": list(current_rank[1]),
        **current_graph,
        "sweeps": sweeps,
        "evaluations": evaluations,
        "connected_evaluations": connected_evaluations,
    }


def select_state_frontier_v45(
    sequence: str, v42_record: dict, parallel: bool = True
) -> dict:
    sequence = validate_sequence(sequence)
    if v42_record.get("schema") != "fold-protein-selected-frontier/v42":
        raise RuntimeError("V45 requires the sealed V42 connected frontier")
    if v42_record.get("sequence") != sequence:
        raise RuntimeError("V45 sequence differs from its V42 parent")
    parents = v42_record.get("frontier", [])
    if (v42_record.get("connected_frontier_count")
            != EXPECTED_CONNECTED_PARENTS
            or len(parents) != EXPECTED_CONNECTED_PARENTS):
        raise RuntimeError("V45 requires all three V42 connected parents")
    if (AXIS_VALUE_COUNT != 24
            or len(DESCENT_ORDERS) != EXPECTED_DESCENT_ORDERS):
        raise RuntimeError("V45 complete boundary-axis grammar drifted")
    blocks = _blocks_from_record(v42_record)
    seeds = []
    for row in parents:
        path = tuple(row["path"])
        if (len(path) != len(sequence) - 1
                or row.get("graph_components") != 1):
            raise RuntimeError("V45 V42 parent identity drifted")
        seeds.append((f'v42_mask_{row["mask"]}', path))
    if len({path for _, path in seeds}) != EXPECTED_CONNECTED_PARENTS:
        raise RuntimeError("V45 connected parent frontier collapsed")

    jobs = [
        (label, path, direction, axis_order)
        for label, path in seeds
        for direction, axis_order in DESCENT_ORDERS
    ]
    if len(jobs) != EXPECTED_FIXED_POINT_TRACES:
        raise RuntimeError("V45 did not generate the complete crossed grammar")
    if parallel:
        with ProcessPoolExecutor(
            max_workers=PARALLEL_WORKERS,
            mp_context=get_context("fork"),
        ) as executor:
            traces = [
                _connected_coordinate_fixed_point(
                    sequence,
                    path,
                    blocks,
                    label,
                    direction,
                    axis_order,
                    executor=executor,
                )
                for label, path, direction, axis_order in jobs
            ]
    else:
        traces = [
            _connected_coordinate_fixed_point(
                sequence, path, blocks, label, direction, axis_order
            )
            for label, path, direction, axis_order in jobs
        ]
    coverage = {
        (row["seed"], row["direction"], tuple(row["axis_order"]))
        for row in traces
    }
    expected_coverage = {
        (label, direction, axis_order)
        for label, _ in seeds
        for direction, axis_order in DESCENT_ORDERS
    }
    if coverage != expected_coverage:
        raise RuntimeError("V45 boundary-axis coverage drifted")

    distinct = {}
    for row in traces:
        path = tuple(row["path"])
        distinct.setdefault(path, []).append({
            "seed": row["seed"],
            "direction": row["direction"],
            "axis_order": row["axis_order"],
        })
    frontier = []
    for path, source_orders in sorted(distinct.items()):
        ranked = _connected_cycle_rank(sequence, path, blocks)
        if ranked is None:
            raise RuntimeError("V45 fixed point lost connectedness")
        rank, graph = ranked
        frontier.append({
            "states": list(path) + [CANONICAL_STATE],
            "source_orders": source_orders,
            "cycle_distance_to_one": rank[0],
            "rank_key": list(rank[1]),
            **graph,
        })
    return {
        "connected_parent_count": len(seeds),
        "axis_value_count": AXIS_VALUE_COUNT,
        "descent_order_count": len(DESCENT_ORDERS),
        "fixed_point_trace_count": len(traces),
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
