#!/usr/bin/env python3
"""V41: complete connected-component cube plus paired-state descent.

The two sealed V40 fixed points define a disagreement set on the registered
linear peptide chain. Its maximal connected components are unique. V41 emits
every binary assignment of those complete components, reconciles the complete
cube under the unchanged admitted V3 order, and then continues the selected
path through the already-admitted 576-state N-to-C fixed-point descent.
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
from tools.blind_24_lattice_selector_v38 import _rank
from tools.blind_24_lattice_selector_v40 import (
    PARALLEL_WORKERS,
    _paired_fixed_point,
)


EXPECTED_DISAGREEMENTS = 42
EXPECTED_COMPONENTS = 13
EXPECTED_CUBE_CANDIDATES = 8192


def maximal_disagreement_components(left: tuple[int, ...],
                                    right: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    if len(left) != len(right):
        raise ValueError("V41 fixed-point lengths differ")
    positions = [index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1]]
    components: list[list[int]] = []
    for position in positions:
        if not components or position != components[-1][-1] + 1:
            components.append([position])
        else:
            components[-1].append(position)
    return tuple(tuple(component) for component in components)


def component_cube_candidate(left: tuple[int, ...], right: tuple[int, ...],
                             components: tuple[tuple[int, ...], ...],
                             mask: int) -> tuple[int, ...]:
    if not 0 <= mask < (1 << len(components)):
        raise ValueError("V41 component mask is outside the complete cube")
    path = list(left)
    for component_index, component in enumerate(components):
        source = right if mask & (1 << component_index) else left
        for residue in component:
            path[residue] = source[residue]
    return tuple(path)


def _rank_cube_candidate(task):
    sequence, left, right, components, mask = task
    path = component_cube_candidate(left, right, components, mask)
    return _rank(sequence, path), path, mask


def select_state_path_v41(sequence: str, v40_record: dict,
                          parallel: bool = True) -> dict:
    sequence = validate_sequence(sequence)
    if v40_record.get("schema") != "fold-protein-selected-states/v40":
        raise RuntimeError("V41 requires the admitted sealed V40 fixed-point grammar")
    if v40_record.get("sequence") != sequence:
        raise RuntimeError("V41 sequence differs from its registered V40 parent")
    traces = v40_record.get("fixed_point_trace", [])
    by_seed = {row["seed"]: tuple(row["path"]) for row in traces}
    if set(by_seed) != {"v38_parent", "v39_causal_child"}:
        raise RuntimeError("V41 did not receive both sealed V40 lineage fixed points")
    left, right = by_seed["v38_parent"], by_seed["v39_causal_child"]
    components = maximal_disagreement_components(left, right)
    disagreement_count = sum(len(component) for component in components)
    candidate_count = 1 << len(components)
    if (disagreement_count != EXPECTED_DISAGREEMENTS
            or len(components) != EXPECTED_COMPONENTS
            or candidate_count != EXPECTED_CUBE_CANDIDATES):
        raise RuntimeError("V41 registered component-cube census drifted")

    tasks = (
        (sequence, left, right, components, mask)
        for mask in range(candidate_count)
    )
    if parallel:
        with ProcessPoolExecutor(
                max_workers=PARALLEL_WORKERS,
                mp_context=get_context("fork")) as executor:
            ranked = list(executor.map(
                _rank_cube_candidate, tasks, chunksize=PARALLEL_WORKERS))
            selected_rank, selected_path, selected_mask = min(
                ranked, key=lambda item: item[0])
            fixed_point = _paired_fixed_point(
                sequence, selected_path, "v41_component_cube", executor=executor)
    else:
        ranked = list(map(_rank_cube_candidate, tasks))
        selected_rank, selected_path, selected_mask = min(
            ranked, key=lambda item: item[0])
        fixed_point = _paired_fixed_point(
            sequence, selected_path, "v41_component_cube")

    final_path = tuple(fixed_point["path"])
    states = list(final_path) + [CANONICAL_STATE]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    cube_trace = [
        {"mask": mask, "rank_key": list(rank[0])}
        for rank, _, mask in ranked
    ]
    return {
        "states": states,
        "atoms": atoms,
        "parent_v40_states": v40_record["states"],
        "parent_fixed_points": [list(left), list(right)],
        "disagreement_count": disagreement_count,
        "components": [list(component) for component in components],
        "component_count": len(components),
        "component_cube_candidates": candidate_count,
        "component_cube_trace": cube_trace,
        "selected_component_mask": selected_mask,
        "selected_component_rank": list(selected_rank[0]),
        "paired_fixed_point": fixed_point,
        "cube_evaluations": len(ranked),
        "paired_evaluations": fixed_point["evaluations"],
        "total_evaluations": len(ranked) + fixed_point["evaluations"],
        "parallel_workers": PARALLEL_WORKERS if parallel else 0,
        "final_key": list(_rank(sequence, final_path)[0]),
    }
