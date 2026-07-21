#!/usr/bin/env python3
"""V38: complete one-coordinate fixed-point descent from the V37 parent.

Every active phi and psi coordinate is scanned across all 24 counted lattice
values while every other coordinate is held fixed.  Both chain directions and
both permutations of the two coordinate axes are executed independently.  Each
of the four descents repeats until a complete sweep makes no change under the
unchanged V3 total order.  The parent and all four fixed points are reconciled
under that same order.  There is no beam, cutoff, comparison input or new score.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from itertools import permutations, product
from multiprocessing import get_context

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    LATTICE_DEGREES,
    _candidate_key,
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)
from tools.blind_24_lattice_selector_v37 import select_state_path_v37


AXIS_VALUE_COUNT = len(LATTICE_DEGREES)
COORDINATE_AXES = (0, 1)
CHAIN_DIRECTIONS = ("n_to_c", "c_to_n")
AXIS_ORDERS = tuple(permutations(COORDINATE_AXES))
DESCENT_ORDERS = tuple(product(CHAIN_DIRECTIONS, AXIS_ORDERS))
PAIRED_STATE_COUNT = AXIS_VALUE_COUNT ** len(COORDINATE_AXES)


def _replace_coordinate(state: int, axis: int, value: int) -> int:
    phi_index, psi_index = divmod(state, AXIS_VALUE_COUNT)
    if axis == 0:
        phi_index = value
    elif axis == 1:
        psi_index = value
    else:
        raise ValueError(f"unsupported coordinate axis: {axis}")
    return phi_index * AXIS_VALUE_COUNT + psi_index


def _rank(sequence: str, path: tuple[int, ...]):
    return (_candidate_key(sequence, list(path)), path)


def _coordinate_fixed_point(sequence: str, seed: tuple[int, ...],
                            direction: str, axis_order: tuple[int, int]) -> dict:
    if direction == "n_to_c":
        residues = tuple(range(len(seed)))
    elif direction == "c_to_n":
        residues = tuple(reversed(range(len(seed))))
    else:
        raise ValueError(f"unsupported chain direction: {direction}")
    if axis_order not in AXIS_ORDERS:
        raise ValueError(f"incomplete coordinate-axis order: {axis_order}")

    current = seed
    current_rank = _rank(sequence, current)
    sweeps = []
    evaluations = 0
    while True:
        sweep_start = current
        changed_coordinates = 0
        for residue in residues:
            for axis in axis_order:
                candidates = []
                for value in range(AXIS_VALUE_COUNT):
                    candidate = list(current)
                    candidate[residue] = _replace_coordinate(
                        candidate[residue], axis, value)
                    candidate_path = tuple(candidate)
                    candidates.append((_rank(sequence, candidate_path), candidate_path))
                evaluations += len(candidates)
                winner_rank, winner = min(candidates, key=lambda item: item[0])
                if winner_rank > current_rank:
                    raise RuntimeError("V38 coordinate scan violated monotone descent")
                if winner != current:
                    changed_coordinates += 1
                current, current_rank = winner, winner_rank
        sweeps.append({
            "sweep": len(sweeps) + 1,
            "changed_coordinates": changed_coordinates,
            "rank_key": list(current_rank[0]),
        })
        if current == sweep_start:
            break
    # A second complete sweep is already represented by the terminating row.
    if sweeps[-1]["changed_coordinates"] != 0:
        raise RuntimeError("V38 fixed point returned before a stable complete sweep")
    return {
        "direction": direction,
        "axis_order": list(axis_order),
        "path": list(current),
        "rank_key": list(current_rank[0]),
        "sweeps": sweeps,
        "evaluations": evaluations,
    }


def select_state_path_v38(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    if AXIS_VALUE_COUNT != 24 or PAIRED_STATE_COUNT != 576:
        raise RuntimeError("V38 complete paired lattice census did not close")
    if len(DESCENT_ORDERS) != 4:
        raise RuntimeError("V38 did not generate every boundary-axis order")

    parent = select_state_path_v37(sequence)
    seed = tuple(parent["states"][:-1])
    # The complete four-order grammar supplies the worker count; scheduling can
    # alter runtime but cannot alter any independently deterministic descent.
    with ProcessPoolExecutor(
            max_workers=len(DESCENT_ORDERS), mp_context=get_context("fork")) as executor:
        descents = list(executor.map(
            _coordinate_fixed_point,
            (sequence for _ in DESCENT_ORDERS),
            (seed for _ in DESCENT_ORDERS),
            (row[0] for row in DESCENT_ORDERS),
            (row[1] for row in DESCENT_ORDERS),
        ))
    coverage = {(row["direction"], tuple(row["axis_order"])) for row in descents}
    if coverage != set(DESCENT_ORDERS):
        raise RuntimeError("V38 descent-order coverage drifted")

    candidates = [("v37_parent", seed)] + [
        (f"{row['direction']}:{row['axis_order']}", tuple(row["path"]))
        for row in descents
    ]
    selected_label, selected_path = min(
        candidates, key=lambda item: _rank(sequence, item[1]))
    states = list(selected_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "atoms": atoms,
        "parent_states": parent["states"],
        "axis_value_count": AXIS_VALUE_COUNT,
        "paired_state_count": PAIRED_STATE_COUNT,
        "descent_order_count": len(DESCENT_ORDERS),
        "parallel_workers": len(DESCENT_ORDERS),
        "descent_trace": descents,
        "total_coordinate_evaluations": sum(row["evaluations"] for row in descents),
        "selected_descent": selected_label,
        "final_key": list(_rank(sequence, selected_path)[0]),
    }
