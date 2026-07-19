#!/usr/bin/env python3
"""Exact successor continuity for assembled backbone hydrogen-bond topology.

V13 constitutes unit-capacity alpha and inter-strand hydrogen-bond pairs. This
module derives the next discrete relation from the chain successor itself: two
held bonds are continuous exactly when both donor residues and both acceptor
residues are adjacent. Alpha continuity preserves direction; inter-strand
continuity admits the two forced orientations, parallel and antiparallel.

The relation contains no distance threshold, fitted energy, target, template,
weight, reward, learned quantity, or tunable span. One is the successor of the
integer residue order, not an imported parameter.
"""
from __future__ import annotations

from itertools import combinations

from tools.backbone_hydrogen_bond_constitution_v2 import (
    TOPOLOGY_CLASSES, topology_backbone_hydrogen_bond_relation)


SUCCESSOR_DISTANCE = 1
CONTINUITY_CLASSES = ("alpha", "interstrand")


def verify_hydrogen_bond_continuity_constitution() -> dict:
    if SUCCESSOR_DISTANCE != 1:
        raise RuntimeError("residue successor did not close to one")
    if tuple(TOPOLOGY_CLASSES) != CONTINUITY_CLASSES:
        raise RuntimeError("hydrogen-bond topology classes drifted")
    return {
        "successor_distance": SUCCESSOR_DISTANCE,
        "topology_classes": list(CONTINUITY_CLASSES),
        "alpha_orientation": "parallel successor",
        "interstrand_orientations": [
            "parallel successor", "antiparallel successor"],
        "distance_cutoff": None,
        "angular_cutoff": None,
        "continuity_weight": None,
        "fitted_energy": None,
        "reward": None,
        "target": None,
    }


HYDROGEN_BOND_CONTINUITY_CENSUS = \
    verify_hydrogen_bond_continuity_constitution()


def _continuous(left: dict, right: dict) -> tuple[bool, str | None]:
    donor_delta = right["donor_residue"] - left["donor_residue"]
    acceptor_delta = right["acceptor_residue"] - left["acceptor_residue"]
    if abs(donor_delta) != SUCCESSOR_DISTANCE or \
            abs(acceptor_delta) != SUCCESSOR_DISTANCE:
        return False, None
    if left["topology"] == "alpha":
        if donor_delta == acceptor_delta:
            return True, "parallel"
        return False, None
    if donor_delta == acceptor_delta:
        return True, "parallel"
    return True, "antiparallel"


def continuity_from_pairs(pairs: list[dict]) -> dict:
    """Count exact successor edges among already assembled unit-capacity pairs."""
    counts = {name: 0 for name in CONTINUITY_CLASSES}
    edges = []
    by_topology = {
        name: sorted(
            (pair for pair in pairs if pair["topology"] == name),
            key=lambda pair: (
                pair["donor_residue"], pair["acceptor_residue"]))
        for name in CONTINUITY_CLASSES
    }
    for topology, rows in by_topology.items():
        for left, right in combinations(rows, 2):
            held, orientation = _continuous(left, right)
            if not held:
                continue
            counts[topology] += 1
            edges.append({
                "topology": topology,
                "orientation": orientation,
                "left": {
                    "donor_residue": left["donor_residue"],
                    "acceptor_residue": left["acceptor_residue"],
                },
                "right": {
                    "donor_residue": right["donor_residue"],
                    "acceptor_residue": right["acceptor_residue"],
                },
            })
    return {
        "relations": {
            name: -counts[name] for name in CONTINUITY_CLASSES},
        "continuity_counts": counts,
        "continuity_edge_count": len(edges),
        "held_pair_counts": {
            name: len(rows) for name, rows in by_topology.items()},
        "edges": edges,
    }


def backbone_hydrogen_bond_continuity_relation(sequence: str, atoms) -> dict:
    assembled = topology_backbone_hydrogen_bond_relation(sequence, atoms)
    return continuity_from_pairs(assembled["pairs"])


def dimensionless_hydrogen_bond_continuity_relations(
        sequence: str, atoms) -> tuple[int, int]:
    relation = backbone_hydrogen_bond_continuity_relation(sequence, atoms)
    return tuple(
        int(relation["relations"][name]) for name in CONTINUITY_CLASSES)
