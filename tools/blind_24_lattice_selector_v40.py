#!/usr/bin/env python3
"""V40: complete paired-state fixed points from the V38/V39 lineage.

V38 and its V39 causal child form the complete binary parent-child lineage.
For each seed, V40 scans every one of the 576 paired phi/psi states at every
active residue in the registered N-to-C direction.  Complete sweeps repeat
until strict fixed point under the unchanged admitted V3 total order.  The
fixed points are then reconciled under that same order. No comparison input,
new score, beam, cutoff, weight or fitted choice enters selection.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)
from tools.blind_24_lattice_selector_v38 import PAIRED_STATE_COUNT, _rank


LINEAGE_SEED_COUNT = 2
CAUSAL_DIRECTION = "n_to_c"
PARALLEL_WORKERS = 24


def _replace_paired_state(path: tuple[int, ...], residue: int,
                          state: int) -> tuple[int, ...]:
    if not 0 <= residue < len(path):
        raise ValueError("V40 residue is outside the active path")
    if not 0 <= state < PAIRED_STATE_COUNT:
        raise ValueError("V40 state is outside the complete paired lattice")
    candidate = list(path)
    candidate[residue] = state
    return tuple(candidate)


def _rank_replacement(task):
    sequence, current, residue, state = task
    candidate = _replace_paired_state(current, residue, state)
    return _rank(sequence, candidate), candidate


def _paired_fixed_point(sequence: str, seed: tuple[int, ...], label: str,
                        executor: ProcessPoolExecutor | None = None) -> dict:
    current = seed
    current_rank = _rank(sequence, current)
    sweeps = []
    evaluations = 0
    while True:
        sweep_start = current
        changed_states = 0
        for residue in range(len(current)):
            tasks = (
                (sequence, current, residue, state)
                for state in range(PAIRED_STATE_COUNT)
            )
            if executor is None:
                candidates = list(map(_rank_replacement, tasks))
            else:
                candidates = list(executor.map(
                    _rank_replacement, tasks, chunksize=PARALLEL_WORKERS))
            evaluations += len(candidates)
            winner_rank, winner = min(candidates, key=lambda item: item[0])
            if winner_rank > current_rank:
                raise RuntimeError("V40 paired scan violated monotone descent")
            if winner != current:
                changed_states += 1
            current, current_rank = winner, winner_rank
        sweeps.append({
            "sweep": len(sweeps) + 1,
            "changed_states": changed_states,
            "rank_key": list(current_rank[0]),
        })
        if current == sweep_start:
            break
    if sweeps[-1]["changed_states"] != 0:
        raise RuntimeError("V40 returned before a stable complete sweep")
    return {
        "seed": label,
        "path": list(current),
        "rank_key": list(current_rank[0]),
        "sweeps": sweeps,
        "evaluations": evaluations,
    }


def _validate_lineage(sequence: str, v38_record: dict,
                      v39_record: dict) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if v38_record.get("schema") != "fold-protein-selected-states/v38":
        raise RuntimeError("V40 requires the admitted sealed V38 parent")
    if v39_record.get("schema") != "fold-protein-selected-states/v39":
        raise RuntimeError("V40 requires the admitted sealed V39 causal child")
    if v38_record.get("sequence") != sequence or v39_record.get("sequence") != sequence:
        raise RuntimeError("V40 lineage sequence drifted")
    if v39_record.get("parent_selected_states") != v38_record.get("states"):
        raise RuntimeError("V40 V39 record is not the registered child of V38")
    parent = tuple(v38_record["states"][:-1])
    child = tuple(v39_record["states"][:-1])
    if len(parent) != len(sequence) - 1 or len(child) != len(sequence) - 1:
        raise RuntimeError("V40 lineage path length drifted")
    if len({parent, child}) != LINEAGE_SEED_COUNT:
        raise RuntimeError("V40 requires the complete distinct binary lineage")
    return parent, child


def select_state_path_v40(sequence: str, v38_record: dict, v39_record: dict,
                          parallel: bool = True) -> dict:
    sequence = validate_sequence(sequence)
    if PAIRED_STATE_COUNT != 576 or PARALLEL_WORKERS != 24:
        raise RuntimeError("V40 complete paired-state census did not close")
    parent, child = _validate_lineage(sequence, v38_record, v39_record)
    seeds = (("v38_parent", parent), ("v39_causal_child", child))

    traces = []
    if parallel:
        with ProcessPoolExecutor(
                max_workers=PARALLEL_WORKERS,
                mp_context=get_context("fork")) as executor:
            for label, seed in seeds:
                traces.append(_paired_fixed_point(
                    sequence, seed, label, executor=executor))
    else:
        traces = [
            _paired_fixed_point(sequence, seed, label)
            for label, seed in seeds
        ]
    if {row["seed"] for row in traces} != {row[0] for row in seeds}:
        raise RuntimeError("V40 did not execute both parent-child lineage seeds")

    distinct = {
        tuple(row["path"]): row for row in traces
    }
    selected_path, selected_trace = min(
        distinct.items(), key=lambda item: _rank(sequence, item[0]))
    states = list(selected_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "atoms": atoms,
        "parent_v38_states": v38_record["states"],
        "parent_v39_states": v39_record["states"],
        "lineage_seed_count": len(seeds),
        "paired_state_count": PAIRED_STATE_COUNT,
        "causal_direction": CAUSAL_DIRECTION,
        "parallel_workers": PARALLEL_WORKERS if parallel else 0,
        "fixed_point_trace": traces,
        "distinct_fixed_points": len(distinct),
        "selected_fixed_point": selected_trace["seed"],
        "total_paired_evaluations": sum(row["evaluations"] for row in traces),
        "final_key": list(_rank(sequence, selected_path)[0]),
    }
