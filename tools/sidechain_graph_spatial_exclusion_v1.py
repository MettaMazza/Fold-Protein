#!/usr/bin/env python3
"""Spatial exclusion from explicit constituted side-chain covalent graphs.

Every residue graph is rooted at generated C-alpha. Integer graph depth moves
outward in the positive L-chiral N/CA/C half-space. At a branch, exact sibling
rank supplies a centred signed offset; successive graph depths alternate the
two remaining generated frame axes. The complete integer embedding is scaled
to n/(n+1) of the generated adjacent C-alpha step, and its atom occupancy unit
is the complementary 1/(n+1) share recorded for each graph atom.

Two non-neighbour residues have one binary hard exclusion when any pair of
their explicitly generated side-chain atoms is separated by less than the
fold-derived half of the generated adjacent C-alpha step. Every atom-pair
encounter is retained in the census. No target, template, rotamer, empirical bond
length, bond angle, residue radius, fitted cutoff, weight, reward, or learned
quantity enters.
"""
from __future__ import annotations

from collections import deque
from functools import lru_cache
import math

import numpy as np

from tools.backbone_hydrogen_bond_constitution_v1 import _residue_backbone
from tools.residue_partition_v1 import AMINO_ACIDS
from tools.residue_steric_constitution_v1 import SIDECHAIN_HEAVY_ATOMS


ROOT = "CA"
NON_NEIGHBOUR_SEPARATION = 2

# Exact covalent side-chain heavy-atom graphs, rooted at C-alpha. Proline's
# return bond to backbone N is outside the side-chain-heavy-atom graph scope.
SIDECHAIN_COVALENT_BONDS = {
    "A": (("CA", "CB"),),
    "C": (("CA", "CB"), ("CB", "SG")),
    "D": (("CA", "CB"), ("CB", "CG"), ("CG", "OD1"), ("CG", "OD2")),
    "E": (("CA", "CB"), ("CB", "CG"), ("CG", "CD"), ("CD", "OE1"), ("CD", "OE2")),
    "F": (("CA", "CB"), ("CB", "CG"), ("CG", "CD1"), ("CG", "CD2"),
          ("CD1", "CE1"), ("CD2", "CE2"), ("CE1", "CZ"), ("CE2", "CZ")),
    "G": (),
    "H": (("CA", "CB"), ("CB", "CG"), ("CG", "ND1"), ("CG", "CD2"),
          ("ND1", "CE1"), ("CD2", "NE2"), ("CE1", "NE2")),
    "I": (("CA", "CB"), ("CB", "CG1"), ("CB", "CG2"), ("CG1", "CD1")),
    "K": (("CA", "CB"), ("CB", "CG"), ("CG", "CD"), ("CD", "CE"), ("CE", "NZ")),
    "L": (("CA", "CB"), ("CB", "CG"), ("CG", "CD1"), ("CG", "CD2")),
    "M": (("CA", "CB"), ("CB", "CG"), ("CG", "SD"), ("SD", "CE")),
    "N": (("CA", "CB"), ("CB", "CG"), ("CG", "OD1"), ("CG", "ND2")),
    "P": (("CA", "CB"), ("CB", "CG"), ("CG", "CD")),
    "Q": (("CA", "CB"), ("CB", "CG"), ("CG", "CD"), ("CD", "OE1"), ("CD", "NE2")),
    "R": (("CA", "CB"), ("CB", "CG"), ("CG", "CD"), ("CD", "NE"),
          ("NE", "CZ"), ("CZ", "NH1"), ("CZ", "NH2")),
    "S": (("CA", "CB"), ("CB", "OG")),
    "T": (("CA", "CB"), ("CB", "OG1"), ("CB", "CG2")),
    "V": (("CA", "CB"), ("CB", "CG1"), ("CB", "CG2")),
    "W": (("CA", "CB"), ("CB", "CG"), ("CG", "CD1"), ("CG", "CD2"),
          ("CD1", "NE1"), ("CD2", "CE2"), ("CD2", "CE3"),
          ("NE1", "CE2"), ("CE2", "CZ2"), ("CE3", "CZ3"),
          ("CZ2", "CH2"), ("CZ3", "CH2")),
    "Y": (("CA", "CB"), ("CB", "CG"), ("CG", "CD1"), ("CG", "CD2"),
          ("CD1", "CE1"), ("CD2", "CE2"), ("CE1", "CZ"),
          ("CE2", "CZ"), ("CZ", "OH")),
}


@lru_cache(maxsize=None)
def _adjacency(residue: str) -> dict[str, set[str]]:
    nodes = {ROOT, *SIDECHAIN_HEAVY_ATOMS[residue]}
    adjacency = {node: set() for node in nodes}
    for left, right in SIDECHAIN_COVALENT_BONDS[residue]:
        if left not in nodes or right not in nodes or left == right:
            raise RuntimeError(f"invalid side-chain bond in {residue}: {left}-{right}")
        adjacency[left].add(right)
        adjacency[right].add(left)
    return adjacency


@lru_cache(maxsize=None)
def _integer_graph_embedding(residue: str) -> dict[str, tuple[int, int, int]]:
    atoms = SIDECHAIN_HEAVY_ATOMS[residue]
    if not atoms:
        return {}
    order = {ROOT: -1, **{atom: index for index, atom in enumerate(atoms)}}
    adjacency = _adjacency(residue)
    parent = {ROOT: None}
    depth = {ROOT: 0}
    children = {node: [] for node in adjacency}
    queue = deque([ROOT])
    while queue:
        node = queue.popleft()
        for neighbour in sorted(adjacency[node], key=order.__getitem__):
            if neighbour in parent:
                continue
            parent[neighbour] = node
            depth[neighbour] = depth[node] + 1
            children[node].append(neighbour)
            queue.append(neighbour)
    if set(parent) != set(adjacency):
        raise RuntimeError(f"disconnected side-chain graph for {residue}")

    coordinates = {ROOT: (0, 0, 0)}
    for node in sorted(atoms, key=lambda atom: (depth[atom], order[atom])):
        source = parent[node]
        siblings = children[source]
        rank = siblings.index(node)
        centred = 2 * rank - (len(siblings) - 1)
        x, y, z = coordinates[source]
        if depth[node] % 2:
            y += centred
        else:
            z += centred
        coordinates[node] = (x + 1, y, z)
    return {atom: coordinates[atom] for atom in atoms}


def verify_sidechain_graph_spatial_constitution() -> dict:
    if set(SIDECHAIN_COVALENT_BONDS) != AMINO_ACIDS:
        raise RuntimeError("side-chain covalent graph alphabet does not close")
    graph_rows = {}
    for residue in sorted(AMINO_ACIDS):
        adjacency = _adjacency(residue)
        embedding = _integer_graph_embedding(residue)
        edges = SIDECHAIN_COVALENT_BONDS[residue]
        if residue == "G":
            if edges or embedding:
                raise RuntimeError("glycine did not close as the empty graph")
        elif ROOT not in adjacency or not adjacency[ROOT]:
            raise RuntimeError(f"side-chain graph is not rooted for {residue}")
        graph_rows[residue] = {
            "atoms": list(SIDECHAIN_HEAVY_ATOMS[residue]),
            "bonds": [list(edge) for edge in edges],
            "integer_embedding": {
                atom: list(embedding[atom]) for atom in embedding},
            "branch_atom_count": sum(
                len(neighbours) > 2 for neighbours in adjacency.values()),
            "cycle_rank": len(edges) - len(adjacency) + 1,
        }
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "graphs": graph_rows,
        "chirality": "L positive cross(CA-to-N, CA-to-C) half-space",
        "reach": "n/(n+1) of generated adjacent C-alpha step",
        "atom_occupancy_unit": "1/(n+1) of generated adjacent C-alpha step",
        "pair_exclusion_unit": "1/2 fold of generated adjacent C-alpha step",
        "hard_exclusion_unit": "one non-neighbour residue pair with at least one atom encounter",
        "empirical_bond_length": None,
        "empirical_bond_angle": None,
        "empirical_radius": None,
        "fitted_cutoff": None,
        "rotamer": None,
        "reward": None,
        "target": None,
    }


SIDECHAIN_GRAPH_SPATIAL_CENSUS = verify_sidechain_graph_spatial_constitution()


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm <= 0:
        raise RuntimeError("side-chain graph frame is degenerate")
    return np.asarray(vector, dtype=float) / norm


def generated_sidechain_graph_points(sequence: str, atoms) -> dict[int, dict]:
    sequence = str(sequence).strip().upper()
    if set(sequence) - AMINO_ACIDS:
        raise ValueError("unsupported residue in side-chain graph relation")
    rows = _residue_backbone(sequence, atoms)
    if len(rows) != len(sequence):
        raise RuntimeError("one generated backbone frame is required per residue")
    if len(rows) < 2:
        return {}
    ca = np.asarray([row["CA"] for row in rows], dtype=float)
    adjacent_d2 = np.sum(np.diff(ca, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("side-chain graph relation received a degenerate step")
    step = math.sqrt(step_d2)

    result = {}
    for index, (residue, row) in enumerate(zip(sequence, rows)):
        graph = _integer_graph_embedding(residue)
        count = len(graph)
        if count == 0:
            continue
        outward = _unit(np.cross(row["N"] - row["CA"], row["C"] - row["CA"]))
        tangent = _unit(row["C"] - row["CA"])
        binormal = _unit(np.cross(outward, tangent))
        raw = {
            atom: (xyz[0] * outward + xyz[1] * tangent + xyz[2] * binormal)
            for atom, xyz in graph.items()}
        maximum = max(float(np.linalg.norm(vector)) for vector in raw.values())
        reach = step * count / (count + 1)
        points = {
            atom: row["CA"] + vector * (reach / maximum)
            for atom, vector in raw.items()}
        result[index] = {
            "residue": residue,
            "points": points,
            "atom_count": count,
            "occupancy_unit": step / (count + 1),
            "step_d2": step_d2,
        }
    return result


def sidechain_graph_spatial_exclusion_relation(sequence: str, atoms) -> dict:
    sequence = str(sequence).strip().upper()
    graphs = generated_sidechain_graph_points(sequence, atoms)
    excluded_pairs = []
    atom_encounters = 0
    for left in sorted(graphs):
        for right in sorted(graphs):
            if right - left < NON_NEIGHBOUR_SEPARATION:
                continue
            left_row, right_row = graphs[left], graphs[right]
            exclusion_d2 = left_row["step_d2"] / 4
            encounters = []
            for left_atom, left_point in left_row["points"].items():
                for right_atom, right_point in right_row["points"].items():
                    distance_d2 = float(np.sum((right_point - left_point) ** 2))
                    if not math.isfinite(distance_d2):
                        raise RuntimeError("side-chain graph separation is non-finite")
                    if distance_d2 < exclusion_d2:
                        encounters.append({
                            "left_atom": left_atom,
                            "right_atom": right_atom,
                            "dimensionless_distance_squared":
                                distance_d2 / exclusion_d2,
                        })
            if not encounters:
                continue
            atom_encounters += len(encounters)
            excluded_pairs.append({
                "left_residue": left + 1,
                "right_residue": right + 1,
                "left_identity": sequence[left],
                "right_identity": sequence[right],
                "atom_encounter_count": len(encounters),
                "encounters": encounters,
            })
    return {
        "hard_exclusions": len(excluded_pairs),
        "excluded_residue_pair_count": len(excluded_pairs),
        "atom_encounter_count": atom_encounters,
        "excluded_pairs": excluded_pairs,
    }
