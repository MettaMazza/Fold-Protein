#!/usr/bin/env python3
"""Sequence-forced degree-two tertiary path over four-residue bodies.

V1 proved that sequence-only body relations can actively direct assembly, but
its unrestricted spanning tree admitted a high-degree hub.  A four-residue
body has exactly two ordered backbone boundaries.  V2 makes that counted fact
structural: Kruskal admission is retained only while each body degree is at
most two and premature cycles are forbidden.  The result is one connected
acyclic degree-two topology -- a Hamiltonian path -- fixed from sequence
before any generated or target coordinate exists.
"""
from __future__ import annotations

from functools import lru_cache
import math
import numpy as np

from tools.blind_24_lattice_selector_v3 import validate_sequence
from tools.constitutional_lexicographic_exclusion_v1 import symmetric_ordinal_vectors
from tools.global_sequence_constraint_graph_v1 import SEGMENT_RESIDUES
from tools.tertiary_segment_body_constitution_v1 import (
    _UnionFind, _edge_counts, _segments)
from tools.residue_steric_constitution_v1 import SIDECHAIN_HEAVY_ATOM_COUNT


@lru_cache(maxsize=None)
def build_tertiary_segment_path(sequence: str):
    sequence = validate_sequence(sequence)
    segments = _segments(len(sequence))
    if len(segments) <= 1:
        return tuple()
    pairs = [(left, right) for left in range(len(segments))
             for right in range(left + 1, len(segments))]
    rows, raw = [], {}
    for left, right in pairs:
        hydrophobic, opposite, like, body = _edge_counts(
            sequence, segments[left], segments[right])
        identity = (left, right)
        rows.append(((0,), (-opposite, -hydrophobic, like, -body), identity))
        raw[identity] = (hydrophobic, opposite, like, body)
    vectors = symmetric_ordinal_vectors(rows)
    ordered = sorted(pairs, key=lambda pair: (vectors[pair], pair))
    union, degree, selected = _UnionFind(len(segments)), [0] * len(segments), []
    for left, right in ordered:
        if degree[left] == 2 or degree[right] == 2:
            continue
        if not union.join(left, right):
            continue
        degree[left] += 1
        degree[right] += 1
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
        })
        if len(selected) == len(segments) - 1:
            break
    if len(selected) != len(segments) - 1 or max(degree) > 2:
        raise RuntimeError("tertiary segment path did not close")
    return tuple(selected)


def verify_tertiary_segment_path_constitution(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    segments = _segments(len(sequence))
    topology = build_tertiary_segment_path(sequence)
    degree = [0] * len(segments)
    for edge in topology:
        for node in edge["segments"]:
            degree[node] += 1
    return {
        "residue_count": len(sequence), "segment_residues": SEGMENT_RESIDUES,
        "segment_count": len(segments), "path_edge_count": len(topology),
        "expected_path_edge_count": max(0, len(segments) - 1),
        "connected_acyclic_degree_two": (
            len(topology) == max(0, len(segments) - 1)
            and (not degree or max(degree) <= 2)),
        "body_boundary_capacity": 2, "body_degrees": degree,
        "orientation_symmetry": ["parallel", "antiparallel"],
        "target": None, "template": None, "fitted_cutoff": None,
        "energy": None, "weight": None, "reward": None,
        "trained_parameter": None,
    }


def tertiary_segment_path_relation(sequence: str, atoms) -> dict:
    sequence = validate_sequence(sequence)
    coordinates = np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)
    if coordinates.shape != (len(sequence), 3):
        raise RuntimeError("tertiary path residue/coordinate census did not close")
    topology = build_tertiary_segment_path(sequence)
    if len(coordinates) < 2:
        return {"objectives": [], "objective_names": [], "edges": []}
    adjacent_d2 = np.sum(np.diff(coordinates, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("tertiary path received a degenerate spatial One")
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
            raise RuntimeError("tertiary segment path axis is degenerate")
        alignment = abs(float(np.dot(left_axis, right_axis)) / norms)
        orientation_deficit = 1.0 - alignment
        total_deficit += deficit
        total_orientation_deficit += orientation_deficit
        objectives.extend((deficit, orientation_deficit))
        rows.append({**edge, "supported_body_capacity": supported,
                     "support_deficit": deficit,
                     "unsigned_axis_alignment": alignment,
                     "orientation_deficit": orientation_deficit})
    return {
        "objectives": [total_deficit, total_orientation_deficit] + objectives,
        "objective_names": ["path_support_deficit", "path_orientation_deficit"]
            + [name for index in range(len(rows))
               for name in (f"path_edge_{index}_support_deficit",
                             f"path_edge_{index}_orientation_deficit")],
        "path_support_deficit": total_deficit,
        "path_orientation_deficit": total_orientation_deficit,
        "edges": rows, "spatial_one_squared": step_d2,
    }
