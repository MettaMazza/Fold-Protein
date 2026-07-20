#!/usr/bin/env python3
"""Counted bounded-degree frontier for sequence-forced tertiary bodies.

One four-residue body has two ordered backbone boundaries and four constituent
residues.  The complete nonempty integer interval between those counted facts
is therefore degree capacity 2, 3 and 4.  V3 constructs all three ordinal
Kruskal closures from sequence before coordinates exist and retains them as a
frontier; no one topology is privileged by an agent-selected degree.
"""
from __future__ import annotations

from functools import lru_cache
import math
import numpy as np

from tools.blind_24_lattice_selector_v3 import validate_sequence
from tools.constitutional_lexicographic_exclusion_v1 import symmetric_ordinal_vectors
from tools.global_sequence_constraint_graph_v1 import SEGMENT_RESIDUES
from tools.residue_steric_constitution_v1 import SIDECHAIN_HEAVY_ATOM_COUNT
from tools.tertiary_segment_body_constitution_v1 import (
    _UnionFind, _edge_counts, _segments)

MINIMUM_BODY_DEGREE = 2
MAXIMUM_BODY_DEGREE = SEGMENT_RESIDUES
DEGREE_FRONTIER = tuple(range(MINIMUM_BODY_DEGREE, MAXIMUM_BODY_DEGREE + 1))


@lru_cache(maxsize=None)
def build_bounded_tertiary_topology(sequence: str, degree_capacity: int):
    sequence = validate_sequence(sequence)
    if degree_capacity not in DEGREE_FRONTIER:
        raise ValueError("degree capacity is outside the counted frontier")
    segments = _segments(len(sequence))
    if len(segments) <= 1:
        return tuple()
    pairs = [(left, right) for left in range(len(segments))
             for right in range(left + 1, len(segments))]
    rows, raw = [], {}
    for left, right in pairs:
        counts = _edge_counts(sequence, segments[left], segments[right])
        hydrophobic, opposite, like, body = counts
        identity = (left, right)
        rows.append(((0,), (-opposite, -hydrophobic, like, -body), identity))
        raw[identity] = counts
    vectors = symmetric_ordinal_vectors(rows)
    ordered = sorted(pairs, key=lambda pair: (vectors[pair], pair))
    union, degrees, selected = _UnionFind(len(segments)), [0] * len(segments), []
    for left, right in ordered:
        if degrees[left] == degree_capacity or degrees[right] == degree_capacity:
            continue
        if not union.join(left, right):
            continue
        degrees[left] += 1
        degrees[right] += 1
        hydrophobic, opposite, like, body = raw[(left, right)]
        selected.append({
            "segments": [left, right],
            "left_residues": [index + 1 for index in segments[left]],
            "right_residues": [index + 1 for index in segments[right]],
            "hydrophobic_capacity": hydrophobic,
            "opposite_charge_capacity": opposite,
            "like_charge_capacity": like,
            "body_capacity": body,
            "ordinal_vector": list(vectors[(left, right)]),
            "degree_capacity": degree_capacity,
        })
        if len(selected) == len(segments) - 1:
            break
    if len(selected) != len(segments) - 1 or max(degrees) > degree_capacity:
        raise RuntimeError("bounded tertiary topology did not close")
    return tuple(selected)


def verify_tertiary_topology_frontier(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    segments = _segments(len(sequence))
    rows = []
    for capacity in DEGREE_FRONTIER:
        topology = build_bounded_tertiary_topology(sequence, capacity)
        degrees = [0] * len(segments)
        for edge in topology:
            for node in edge["segments"]:
                degrees[node] += 1
        rows.append({"degree_capacity": capacity,
                     "edge_count": len(topology), "body_degrees": degrees,
                     "connected_acyclic": len(topology) == max(0, len(segments) - 1),
                     "capacity_respected": not degrees or max(degrees) <= capacity})
    return {
        "residue_count": len(sequence), "segment_residues": SEGMENT_RESIDUES,
        "segment_count": len(segments), "degree_frontier": list(DEGREE_FRONTIER),
        "topologies": rows, "frontier_complete": all(
            row["connected_acyclic"] and row["capacity_respected"] for row in rows),
        "target": None, "template": None, "fitted_cutoff": None,
        "energy": None, "weight": None, "reward": None,
        "trained_parameter": None,
    }


def bounded_tertiary_relation(sequence: str, atoms, degree_capacity: int) -> dict:
    sequence = validate_sequence(sequence)
    coordinates = np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)
    if coordinates.shape != (len(sequence), 3):
        raise RuntimeError("bounded topology residue/coordinate census did not close")
    topology = build_bounded_tertiary_topology(sequence, degree_capacity)
    if len(coordinates) < 2:
        return {"objectives": [], "objective_names": [], "edges": []}
    adjacent_d2 = np.sum(np.diff(coordinates, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("bounded topology received a degenerate spatial One")
    step, segments = math.sqrt(step_d2), _segments(len(sequence))
    objectives, rows = [], []
    total_deficit, total_orientation_deficit = 0, 0.0
    for edge in topology:
        left_index, right_index = edge["segments"]
        left, right = segments[left_index], segments[right_index]
        possible = supported = 0
        for i in left:
            for j in right:
                a = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[i]]
                b = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[j]]
                capacity = (a + 1) * (b + 1)
                possible += capacity
                bridge = step * a / (a + 1) + step + step * b / (b + 1)
                delta = coordinates[j] - coordinates[i]
                if float(np.dot(delta, delta)) <= bridge * bridge:
                    supported += capacity
        deficit = possible - supported
        left_axis = coordinates[left[-1]] - coordinates[left[0]]
        right_axis = coordinates[right[-1]] - coordinates[right[0]]
        norms = float(np.linalg.norm(left_axis) * np.linalg.norm(right_axis))
        if norms == 0:
            raise RuntimeError("bounded topology body axis is degenerate")
        alignment = abs(float(np.dot(left_axis, right_axis)) / norms)
        orientation_deficit = 1.0 - alignment
        total_deficit += deficit
        total_orientation_deficit += orientation_deficit
        objectives.extend((deficit, orientation_deficit))
        rows.append({**edge, "supported_body_capacity": supported,
                     "support_deficit": deficit,
                     "unsigned_axis_alignment": alignment,
                     "orientation_deficit": orientation_deficit})
    prefix = f"degree_{degree_capacity}"
    return {
        "degree_capacity": degree_capacity,
        "objectives": [total_deficit, total_orientation_deficit] + objectives,
        "objective_names": [f"{prefix}_support_deficit",
                            f"{prefix}_orientation_deficit"]
            + [name for index in range(len(rows))
               for name in (f"{prefix}_edge_{index}_support_deficit",
                             f"{prefix}_edge_{index}_orientation_deficit")],
        "support_deficit": total_deficit,
        "orientation_deficit": total_orientation_deficit,
        "edges": rows, "spatial_one_squared": step_d2,
    }
