#!/usr/bin/env python3
"""Sequence-forced tertiary topology over four-residue bodies.

The existing four-residue orientation unit supplies the bodies.  Every pair
of bodies carries exact integer capacities counted from covalent side-chain
atoms, hydrophobic membership and formal charge.  A permutation-invariant
ordinal relation orders those integer vectors and Kruskal closure retains the
first connected, acyclic topology.  Coordinates do not enter topology
construction.

For a generated chain, each retained edge measures how much of its complete
cross-body atom capacity is supported by the existing side-chain reach plus
the generated adjacent C-alpha spatial One.  Body-axis alignment is unsigned:
parallel and antiparallel frames are the two orientations of one relation.
No target, template, fitted cutoff, energy, scalar weight, reward, trained
parameter or contact label enters.
"""
from __future__ import annotations

from functools import lru_cache
import math
import numpy as np

from tools.blind_24_lattice_selector_v3 import validate_sequence
from tools.constitutional_lexicographic_exclusion_v1 import symmetric_ordinal_vectors
from tools.global_sequence_constraint_graph_v1 import SEGMENT_RESIDUES
from tools.residue_charge_constitution_v1 import CHARGE_SIGN
from tools.residue_partition_v1 import HYDROPHOBIC_PACKING
from tools.residue_steric_constitution_v1 import SIDECHAIN_HEAVY_ATOM_COUNT


def _segments(length: int):
    return tuple(tuple(range(start, min(start + SEGMENT_RESIDUES, length)))
                 for start in range(0, length, SEGMENT_RESIDUES))


class _UnionFind:
    def __init__(self, count):
        self.parent = list(range(count))

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def join(self, left, right):
        left, right = self.find(left), self.find(right)
        if left == right:
            return False
        self.parent[right] = left
        return True


def _edge_counts(sequence, left, right):
    hydrophobic = opposite = like = body = 0
    for i in left:
        for j in right:
            a = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[i]]
            b = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[j]]
            capacity = a * b
            body += (a + 1) * (b + 1)
            if (sequence[i] in HYDROPHOBIC_PACKING
                    and sequence[j] in HYDROPHOBIC_PACKING):
                hydrophobic += capacity
            product = CHARGE_SIGN[sequence[i]] * CHARGE_SIGN[sequence[j]]
            if product < 0:
                opposite += capacity
            elif product > 0:
                like += capacity
    return hydrophobic, opposite, like, body


@lru_cache(maxsize=None)
def build_tertiary_segment_topology(sequence: str):
    sequence = validate_sequence(sequence)
    segments = _segments(len(sequence))
    if len(segments) <= 1:
        return tuple()
    pairs = [(left, right) for left in range(len(segments))
             for right in range(left + 1, len(segments))]
    rows = []
    raw = {}
    for left, right in pairs:
        counts = _edge_counts(sequence, segments[left], segments[right])
        hydrophobic, opposite, like, body = counts
        identity = (left, right)
        # Attractions are negated so lower ordinal rank is stronger; like
        # charge remains positive. Body capacity closes otherwise equal rows.
        rows.append(((0,), (-opposite, -hydrophobic, like, -body), identity))
        raw[identity] = counts
    vectors = symmetric_ordinal_vectors(rows)
    ordered = sorted(pairs, key=lambda pair: (vectors[pair], pair))
    union = _UnionFind(len(segments))
    selected = []
    for left, right in ordered:
        if union.join(left, right):
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
    if len(selected) != len(segments) - 1:
        raise RuntimeError("tertiary segment topology did not close to a tree")
    return tuple(selected)


def verify_tertiary_segment_body_constitution(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    segments = _segments(len(sequence))
    topology = build_tertiary_segment_topology(sequence)
    return {
        "residue_count": len(sequence),
        "segment_residues": SEGMENT_RESIDUES,
        "segment_count": len(segments),
        "tree_edge_count": len(topology),
        "expected_tree_edge_count": max(0, len(segments) - 1),
        "connected_acyclic": len(topology) == max(0, len(segments) - 1),
        "orientation_symmetry": ["parallel", "antiparallel"],
        "target": None, "template": None, "fitted_cutoff": None,
        "energy": None, "weight": None, "reward": None,
        "trained_parameter": None,
    }


def _ca_coordinates(atoms):
    coordinates = np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"], dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1:] != (3,):
        raise RuntimeError("tertiary bodies require one generated C-alpha path")
    return coordinates


def tertiary_segment_body_relation(sequence: str, atoms) -> dict:
    sequence = validate_sequence(sequence)
    coordinates = _ca_coordinates(atoms)
    if len(coordinates) != len(sequence):
        raise RuntimeError("tertiary body residue/coordinate census did not close")
    topology = build_tertiary_segment_topology(sequence)
    if len(coordinates) < 2:
        return {"objectives": [], "objective_names": [], "edges": []}
    adjacent_d2 = np.sum(np.diff(coordinates, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("tertiary bodies received a degenerate spatial One")
    step = math.sqrt(step_d2)
    segments = _segments(len(sequence))
    objectives = []
    rows = []
    total_deficit = 0
    total_orientation_deficit = 0.0
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
                bridge = (step * a / (a + 1) + step
                          + step * b / (b + 1))
                delta = coordinates[j] - coordinates[i]
                if float(np.dot(delta, delta)) <= bridge * bridge:
                    supported += capacity
        deficit = possible - supported
        left_axis = coordinates[left[-1]] - coordinates[left[0]]
        right_axis = coordinates[right[-1]] - coordinates[right[0]]
        left_norm = float(np.linalg.norm(left_axis))
        right_norm = float(np.linalg.norm(right_axis))
        if left_norm == 0 or right_norm == 0:
            raise RuntimeError("tertiary segment body axis is degenerate")
        alignment = abs(float(np.dot(
            left_axis / left_norm, right_axis / right_norm)))
        orientation_deficit = 1.0 - alignment
        total_deficit += deficit
        total_orientation_deficit += orientation_deficit
        objectives.extend((deficit, orientation_deficit))
        rows.append({
            **edge,
            "supported_body_capacity": supported,
            "support_deficit": deficit,
            "unsigned_axis_alignment": alignment,
            "orientation_deficit": orientation_deficit,
        })
    return {
        "objectives": [total_deficit, total_orientation_deficit] + objectives,
        "objective_names": ["tree_support_deficit", "tree_orientation_deficit"]
            + [name for index in range(len(rows))
               for name in (f"tree_edge_{index}_support_deficit",
                             f"tree_edge_{index}_orientation_deficit")],
        "tree_support_deficit": total_deficit,
        "tree_orientation_deficit": total_orientation_deficit,
        "edges": rows,
        "spatial_one_squared": step_d2,
    }
