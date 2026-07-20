#!/usr/bin/env python3
"""Whole-sequence, target-incapable constraint graph for selector v23.

The graph is fixed by the supplied sequence before a conformation is judged.
Its nodes are residues and its non-neighbour edges carry only already
constituted residue facts: side-chain graph size, hydrophobic membership,
formal charge sign, sequence separation, and four-residue segment identity.

For a generated backbone, the adjacent C-alpha step is the spatial One.  Each
side-chain graph of ``n`` atoms has the existing exact reach ``n/(n+1)`` of
that One.  An edge has geometric support when the generated C-alpha separation
can be bridged by the two constituted reaches and one complete spatial One.
This is a cheap necessary support relation used to propagate whole-chain
domains; the final v23 frontier is still judged by the explicit atom graph.

No target, template, learned quantity, fitted cutoff, reward, scalar mixing
weight, or empirical structure enters this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np

from tools.blind_24_lattice_selector_v3 import validate_sequence
from tools.residue_charge_constitution_v1 import CHARGE_SIGN
from tools.residue_partition_v1 import HYDROPHOBIC_PACKING
from tools.residue_steric_constitution_v1 import SIDECHAIN_HEAVY_ATOM_COUNT


SEGMENT_RESIDUES = 4
NON_NEIGHBOUR_SEPARATION = 2


@dataclass(frozen=True)
class SequenceConstraintEdge:
    left: int
    right: int
    left_atoms: int
    right_atoms: int
    atom_pair_capacity: int
    segment_pair: tuple[int, int]
    hydrophobic_pair: bool
    charge_product: int


@lru_cache(maxsize=None)
def build_sequence_constraint_graph(sequence: str) -> tuple[SequenceConstraintEdge, ...]:
    sequence = validate_sequence(sequence)
    edges = []
    for left in range(len(sequence)):
        for right in range(left + NON_NEIGHBOUR_SEPARATION, len(sequence)):
            left_atoms = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[left]]
            right_atoms = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[right]]
            edges.append(SequenceConstraintEdge(
                left=left,
                right=right,
                left_atoms=left_atoms,
                right_atoms=right_atoms,
                atom_pair_capacity=left_atoms * right_atoms,
                segment_pair=(left // SEGMENT_RESIDUES, right // SEGMENT_RESIDUES),
                hydrophobic_pair=(
                    sequence[left] in HYDROPHOBIC_PACKING
                    and sequence[right] in HYDROPHOBIC_PACKING),
                charge_product=(
                    CHARGE_SIGN[sequence[left]] * CHARGE_SIGN[sequence[right]]),
            ))
    return tuple(edges)


@lru_cache(maxsize=None)
def _compiled_sequence_constraint_graph(sequence: str):
    graph = build_sequence_constraint_graph(sequence)
    segment_pairs = sorted({
        edge.segment_pair for edge in graph
        if edge.segment_pair[0] != edge.segment_pair[1]
        and (edge.hydrophobic_pair or edge.charge_product != 0)})
    segment_index = {pair: index for index, pair in enumerate(segment_pairs)}
    return {
        "graph": graph,
        "left": np.asarray([edge.left for edge in graph], dtype=np.int64),
        "right": np.asarray([edge.right for edge in graph], dtype=np.int64),
        "left_atoms": np.asarray([edge.left_atoms for edge in graph], dtype=np.int64),
        "right_atoms": np.asarray([edge.right_atoms for edge in graph], dtype=np.int64),
        "capacity": np.asarray([edge.atom_pair_capacity for edge in graph], dtype=np.int64),
        "hydrophobic": np.asarray([edge.hydrophobic_pair for edge in graph], dtype=bool),
        "opposite": np.asarray([edge.charge_product < 0 for edge in graph], dtype=bool),
        "like": np.asarray([edge.charge_product > 0 for edge in graph], dtype=bool),
        "intersegment": np.asarray([
            edge.segment_pair[0] != edge.segment_pair[1] for edge in graph], dtype=bool),
        "segment_pairs": segment_pairs,
        "segment_group": np.asarray([
            segment_index.get(edge.segment_pair, -1) for edge in graph], dtype=np.int64),
    }


def verify_sequence_constraint_graph(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    graph = build_sequence_constraint_graph(sequence)
    expected = sum(
        len(sequence) - left - NON_NEIGHBOUR_SEPARATION
        for left in range(max(0, len(sequence) - NON_NEIGHBOUR_SEPARATION)))
    if len(graph) != expected:
        raise RuntimeError("complete non-neighbour sequence graph did not close")
    if any(edge.left >= edge.right for edge in graph):
        raise RuntimeError("sequence graph edge orientation did not close")
    segment_pairs = sorted({edge.segment_pair for edge in graph})
    return {
        "residue_count": len(sequence),
        "edge_count": len(graph),
        "segment_residues": SEGMENT_RESIDUES,
        "segment_count": (len(sequence) + SEGMENT_RESIDUES - 1) // SEGMENT_RESIDUES,
        "segment_pair_count": len(segment_pairs),
        "sidechain_reach": "n/(n+1) of generated adjacent C-alpha step",
        "support_bridge": "left reach + spatial One + right reach",
        "target": None,
        "template": None,
        "learned_quantity": None,
        "fitted_cutoff": None,
        "mixing_weight": None,
        "reward": None,
    }


def _ca_coordinates(atoms) -> np.ndarray:
    coordinates = np.asarray(
        [atom["coord"] for atom in atoms if atom["name"] == "CA"],
        dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1:] != (3,):
        raise RuntimeError("constraint graph requires one generated C-alpha path")
    return coordinates


def sequence_constraint_relations(sequence: str, atoms, *, include_rows: bool = True) -> dict:
    """Return exact integer hard/support relations for a generated chain."""
    sequence = validate_sequence(sequence)
    coordinates = _ca_coordinates(atoms)
    if len(coordinates) != len(sequence):
        raise RuntimeError("constraint graph residue/coordinate census did not close")
    if len(sequence) < 2:
        return {
            "backbone_exclusions": 0,
            "objectives": [0, 0, 0, 0, 0, 0],
            "objective_names": [
                "hydrophobic_support_deficit", "opposite_charge_support_deficit",
                "like_charge_support", "intersegment_hydrophobic_support_deficit",
                "intersegment_opposite_charge_support_deficit",
                "intersegment_like_charge_support"],
            "segment_pair_objectives": [],
            "supported_edge_count": 0,
        }

    adjacent_d2 = np.sum(np.diff(coordinates, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("constraint graph received a degenerate spatial One")
    step = math.sqrt(step_d2)
    compiled = _compiled_sequence_constraint_graph(sequence)
    left, right = compiled["left"], compiled["right"]
    delta = coordinates[right] - coordinates[left]
    distance_d2 = np.einsum("ij,ij->i", delta, delta)
    if not np.all(np.isfinite(distance_d2)):
        raise RuntimeError("constraint graph separation is non-finite")
    capacity = compiled["capacity"]
    left_atoms, right_atoms = compiled["left_atoms"], compiled["right_atoms"]
    bridge = (step * left_atoms / (left_atoms + 1)
              + step + step * right_atoms / (right_atoms + 1))
    has_support = (capacity > 0) & (distance_d2 <= bridge * bridge)
    backbone_exclusions = int(np.count_nonzero(distance_d2 < step_d2))
    supported = int(np.count_nonzero(has_support))
    hydrophobic = compiled["hydrophobic"]
    opposite = compiled["opposite"]
    like = compiled["like"]
    intersegment = compiled["intersegment"]

    def total(mask):
        return int(np.sum(capacity[mask], dtype=np.int64))

    hydrophobic_possible = total(hydrophobic)
    hydrophobic_supported = total(hydrophobic & has_support)
    opposite_possible = total(opposite)
    opposite_supported = total(opposite & has_support)
    like_supported = total(like & has_support)
    inter_hydrophobic_possible = total(intersegment & hydrophobic)
    inter_hydrophobic_supported = total(intersegment & hydrophobic & has_support)
    inter_opposite_possible = total(intersegment & opposite)
    inter_opposite_supported = total(intersegment & opposite & has_support)
    inter_like_supported = total(intersegment & like & has_support)

    objectives = [
        hydrophobic_possible - hydrophobic_supported,
        opposite_possible - opposite_supported,
        like_supported,
        inter_hydrophobic_possible - inter_hydrophobic_supported,
        inter_opposite_possible - inter_opposite_supported,
        inter_like_supported,
    ]
    group = compiled["segment_group"]
    group_count = len(compiled["segment_pairs"])
    valid_group = group >= 0
    def grouped(mask):
        return np.bincount(
            group[valid_group & mask], weights=capacity[valid_group & mask],
            minlength=group_count).astype(np.int64)
    hydro_possible_rows = grouped(hydrophobic)
    hydro_supported_rows = grouped(hydrophobic & has_support)
    opposite_possible_rows = grouped(opposite)
    opposite_supported_rows = grouped(opposite & has_support)
    like_supported_rows = grouped(like & has_support)
    segment_pair_objectives = []
    segment_pair_rows = []
    for index, pair in enumerate(compiled["segment_pairs"]):
        values = [
            int(hydro_possible_rows[index] - hydro_supported_rows[index]),
            int(opposite_possible_rows[index] - opposite_supported_rows[index]),
            int(like_supported_rows[index]),
        ]
        segment_pair_objectives.extend(values)
        if include_rows:
            segment_pair_rows.append({"segments": list(pair), "objectives": values})
    return {
        "backbone_exclusions": backbone_exclusions,
        "objectives": objectives,
        "objective_names": [
            "hydrophobic_support_deficit", "opposite_charge_support_deficit",
            "like_charge_support", "intersegment_hydrophobic_support_deficit",
            "intersegment_opposite_charge_support_deficit",
            "intersegment_like_charge_support"],
        "segment_pair_objectives": segment_pair_objectives,
        "segment_pair_rows": segment_pair_rows,
        "supported_edge_count": supported,
        "edge_count": len(compiled["graph"]),
        "spatial_one_squared": step_d2,
    }
