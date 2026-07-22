#!/usr/bin/env python3
"""V42 complete whole-chain backbone contact frontier.

Every V41 component-cube row generates its complete N/CA/C backbone.  The two
sealed V40 rows uniquely partition all 76 residues into maximal equal/disagree
blocks.  A non-neighbour atom pair in the generated half-One-to-One shell adds
an edge between its blocks.  V42 retains every cube row whose block graph has
the graph-theoretic minimum of one connected component.  It emits the complete
frontier and never chooses among retained rows from a target or agent tie-break.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import numpy as np

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE, angles_for_state, build_backbone_coordinates,
    validate_sequence)
from tools.blind_24_lattice_selector_v40 import PARALLEL_WORKERS
from tools.blind_24_lattice_selector_v41 import (
    component_cube_candidate, maximal_disagreement_components)


EXPECTED_DISAGREEMENTS = 42
EXPECTED_DISAGREEMENT_COMPONENTS = 13
EXPECTED_BLOCKS = 26
EXPECTED_CUBE_CANDIDATES = 8192
CONTACT_INNER_SQUARED_NUMERATOR = 1
CONTACT_INNER_SQUARED_DENOMINATOR = 4


def maximal_status_blocks(left: tuple[int, ...], right: tuple[int, ...]):
    if len(left) != len(right):
        raise ValueError("V42 parent state lengths differ")
    blocks: list[tuple[bool, list[int]]] = []
    for residue, (a, b) in enumerate(zip(left, right)):
        disagree = a != b
        if not blocks or blocks[-1][0] != disagree:
            blocks.append((disagree, [residue]))
        else:
            blocks[-1][1].append(residue)
    return tuple((kind, tuple(residues)) for kind, residues in blocks)


def graph_component_count(node_count: int, edges) -> int:
    parent = list(range(node_count))
    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    for left, right in edges:
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left
    return len({find(node) for node in range(node_count)})


def backbone_contact_row(sequence: str, path: tuple[int, ...], blocks) -> dict:
    states = path + (CANONICAL_STATE,)
    atoms = build_backbone_coordinates(
        sequence,
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states])
    residues = [dict() for _ in sequence]
    for atom in atoms:
        residues[atom["resnum"] - 1][atom["name"]] = np.asarray(atom["coord"])
    if any(set(row) != {"N", "CA", "C"} for row in residues):
        raise RuntimeError("V42 requires one complete generated N/CA/C frame per residue")
    ca = np.asarray([row["CA"] for row in residues])
    step_d2 = float(np.mean(np.sum(np.diff(ca, axis=0) ** 2, axis=1)))
    if not np.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("V42 generated adjacent C-alpha One is degenerate")
    block_of = {
        residue: block_index
        for block_index, (_, members) in enumerate(blocks)
        for residue in members
    }
    edges = set()
    residue_pairs = atom_contacts = 0
    for left in range(len(residues)):
        for right in range(left + 2, len(residues)):
            contacts = 0
            for left_point in residues[left].values():
                for right_point in residues[right].values():
                    distance_d2 = float(np.sum((right_point - left_point) ** 2))
                    if step_d2 / CONTACT_INNER_SQUARED_DENOMINATOR <= distance_d2 < step_d2:
                        contacts += 1
            if contacts:
                residue_pairs += 1
                atom_contacts += contacts
                left_block, right_block = block_of[left], block_of[right]
                if left_block != right_block:
                    edges.add(tuple(sorted((left_block, right_block))))
    return {
        "graph_components": graph_component_count(len(blocks), edges),
        "interblock_edges": len(edges),
        "contact_residue_pairs": residue_pairs,
        "contact_atom_pairs": atom_contacts,
        "spatial_one_squared": step_d2,
        "atoms": atoms,
    }


def _evaluate_mask(task):
    sequence, left, right, components, blocks, mask = task
    path = component_cube_candidate(left, right, components, mask)
    row = backbone_contact_row(sequence, path, blocks)
    return {
        "mask": mask, "path": list(path),
        "graph_components": row["graph_components"],
        "interblock_edges": row["interblock_edges"],
        "contact_residue_pairs": row["contact_residue_pairs"],
        "contact_atom_pairs": row["contact_atom_pairs"],
    }


def select_state_frontier_v42(sequence: str, v41_record: dict,
                              parallel: bool = True) -> dict:
    sequence = validate_sequence(sequence)
    if v41_record.get("schema") != "fold-protein-selected-states/v41":
        raise RuntimeError("V42 requires the sealed V41 record")
    if v41_record.get("sequence") != sequence:
        raise RuntimeError("V42 sequence differs from V41")
    left, right = map(tuple, v41_record["parent_fixed_points"])
    components = maximal_disagreement_components(left, right)
    full_left, full_right = left + (CANONICAL_STATE,), right + (CANONICAL_STATE,)
    blocks = maximal_status_blocks(full_left, full_right)
    census = (sum(map(len, components)), len(components), len(blocks),
              sum(kind for kind, _ in blocks), 1 << len(components))
    if census != (EXPECTED_DISAGREEMENTS, EXPECTED_DISAGREEMENT_COMPONENTS,
                  EXPECTED_BLOCKS, EXPECTED_DISAGREEMENT_COMPONENTS,
                  EXPECTED_CUBE_CANDIDATES):
        raise RuntimeError("V42 source-bound block/cube census drifted")
    tasks = ((sequence, left, right, components, blocks, mask)
             for mask in range(EXPECTED_CUBE_CANDIDATES))
    if parallel:
        with ProcessPoolExecutor(max_workers=PARALLEL_WORKERS,
                mp_context=get_context("fork")) as executor:
            trace = list(executor.map(_evaluate_mask, tasks, chunksize=PARALLEL_WORKERS))
    else:
        trace = list(map(_evaluate_mask, tasks))
    frontier = [row for row in trace if row["graph_components"] == 1]
    if not frontier:
        raise RuntimeError("V42 complete cube contains no connected whole-chain graph")
    frontier.sort(key=lambda row: row["mask"])
    for row in frontier:
        detail = backbone_contact_row(sequence, tuple(row["path"]), blocks)
        row["states"] = row["path"] + [CANONICAL_STATE]
        row["atoms"] = detail["atoms"]
        row["spatial_one_squared"] = detail["spatial_one_squared"]
    return {
        "blocks": [{"status": "disagree" if kind else "equal",
                    "residues": [index + 1 for index in members]}
                   for kind, members in blocks],
        "block_count": len(blocks),
        "disagreement_block_count": sum(kind for kind, _ in blocks),
        "equal_block_count": sum(not kind for kind, _ in blocks),
        "component_cube_candidates": len(trace),
        "component_cube_trace": trace,
        "connected_frontier_count": len(frontier),
        "frontier": frontier,
        "parallel_workers": PARALLEL_WORKERS if parallel else 0,
    }
