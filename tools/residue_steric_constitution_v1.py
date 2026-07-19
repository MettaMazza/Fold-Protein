#!/usr/bin/env python3
"""Exact side-chain heavy-atom constitution and scale-free crowding relation.

The 20 registered amino-acid identities determine finite covalent side-chain
heavy-atom graphs.  This module records those graphs explicitly and proves
exhaustive alphabet closure.  It does not import the legacy residue radii,
distance cutoffs, fitted weights, rotamers, targets, or empirical structures.

For two generated non-neighbour residues, the Cartesian product of their
side-chain heavy-atom sets counts the possible atom/atom encounters.  Dividing
that exact count by generated C-alpha separation, normalized by the generated
adjacent step, gives a dimensionless crowding order.  Glycine has the empty
side-chain heavy-atom set and therefore contributes no side-chain crowding.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from tools.residue_partition_v1 import AMINO_ACIDS
except ImportError:  # direct execution from tools/
    from residue_partition_v1 import AMINO_ACIDS


SIDECHAIN_HEAVY_ATOMS = {
    "A": ("CB",),
    "C": ("CB", "SG"),
    "D": ("CB", "CG", "OD1", "OD2"),
    "E": ("CB", "CG", "CD", "OE1", "OE2"),
    "F": ("CB", "CG", "CD1", "CD2", "CE1", "CE2", "CZ"),
    "G": (),
    "H": ("CB", "CG", "ND1", "CD2", "CE1", "NE2"),
    "I": ("CB", "CG1", "CG2", "CD1"),
    "K": ("CB", "CG", "CD", "CE", "NZ"),
    "L": ("CB", "CG", "CD1", "CD2"),
    "M": ("CB", "CG", "SD", "CE"),
    "N": ("CB", "CG", "OD1", "ND2"),
    "P": ("CB", "CG", "CD"),
    "Q": ("CB", "CG", "CD", "OE1", "NE2"),
    "R": ("CB", "CG", "CD", "NE", "CZ", "NH1", "NH2"),
    "S": ("CB", "OG"),
    "T": ("CB", "OG1", "CG2"),
    "V": ("CB", "CG1", "CG2"),
    "W": ("CB", "CG", "CD1", "CD2", "NE1", "CE2", "CE3",
          "CZ2", "CZ3", "CH2"),
    "Y": ("CB", "CG", "CD1", "CD2", "CE1", "CE2", "CZ", "OH"),
}


def verify_steric_constitution() -> dict:
    """Return the exact graph census or halt on alphabet/atom duplication."""
    if set(SIDECHAIN_HEAVY_ATOMS) != AMINO_ACIDS:
        missing = AMINO_ACIDS - set(SIDECHAIN_HEAVY_ATOMS)
        unexpected = set(SIDECHAIN_HEAVY_ATOMS) - AMINO_ACIDS
        raise RuntimeError(
            "side-chain graph constitution does not close; "
            f"missing={''.join(sorted(missing))}; "
            f"unexpected={''.join(sorted(unexpected))}")
    counts = {}
    for residue, atoms in SIDECHAIN_HEAVY_ATOMS.items():
        if len(atoms) != len(set(atoms)):
            raise RuntimeError(
                f"duplicate heavy atom in registered {residue} side chain")
        if any(atom.startswith("H") for atom in atoms):
            raise RuntimeError(
                f"hydrogen entered heavy-atom constitution for {residue}")
        counts[residue] = len(atoms)
    if counts["G"] != 0 or min(counts.values()) != 0:
        raise RuntimeError("glycine did not close as the empty side-chain graph")
    if counts["W"] != max(counts.values()):
        raise RuntimeError("tryptophan did not close as the largest graph census")
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "sidechain_heavy_atoms": {
            residue: list(SIDECHAIN_HEAVY_ATOMS[residue])
            for residue in sorted(AMINO_ACIDS)
        },
        "sidechain_heavy_atom_counts": {
            residue: counts[residue] for residue in sorted(AMINO_ACIDS)
        },
    }


STERIC_CENSUS = verify_steric_constitution()
SIDECHAIN_HEAVY_ATOM_COUNT = {
    residue: len(atoms) for residue, atoms in SIDECHAIN_HEAVY_ATOMS.items()
}


def dimensionless_sidechain_crowding_relation(
        sequence: str, ca_coordinates: np.ndarray) -> float:
    """Return counted side-chain encounters over generated separations."""
    sequence = str(sequence).strip().upper()
    coordinates = np.asarray(ca_coordinates, dtype=float)
    if len(sequence) != len(coordinates):
        raise ValueError("one sequence residue is required per C-alpha coordinate")
    if set(sequence) - AMINO_ACIDS:
        raise ValueError("unsupported residue in steric relation")
    if len(coordinates) < 2:
        return 0.0

    adjacent_d2 = np.sum(np.diff(coordinates, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("steric relation received a degenerate generated step")

    relation = 0.0
    for left in range(len(sequence)):
        left_count = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[left]]
        if left_count == 0:
            continue
        for right in range(left + 2, len(sequence)):
            right_count = SIDECHAIN_HEAVY_ATOM_COUNT[sequence[right]]
            if right_count == 0:
                continue
            distance_d2 = float(np.sum(
                (coordinates[right] - coordinates[left]) ** 2))
            if not math.isfinite(distance_d2) or distance_d2 <= 0:
                raise RuntimeError("steric relation received coincident coordinates")
            relation += (
                left_count * right_count
                * math.sqrt(step_d2 / distance_d2)
            )
    if not math.isfinite(relation):
        raise RuntimeError("steric relation produced a non-finite value")
    return relation
