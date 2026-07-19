#!/usr/bin/env python3
"""Exact residue charge-sign constitution for target-free mode selection.

Lysine/arginine side chains carry positive formal charge and aspartate/
glutamate side chains carry negative formal charge in the registered protein
constitution.  Histidine is left in the uncharged class because its state is
environment-dependent and this zero-parameter relation has no pH input or
fitted fractional charge.  The module proves exhaustive, disjoint coverage of
the same 20-residue alphabet used by the active blind selector.

The geometric relation is a dimensionless Coulomb-sign order over generated
non-neighbour C-alpha separations.  Adjacent generated step length supplies the
only scale.  No dielectric constant, cutoff, fitted weight, or target geometry
is present; negative opposite-sign relation is ordered before positive like-
sign relation.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from tools.residue_partition_v1 import AMINO_ACIDS
except ImportError:  # direct execution from tools/
    from residue_partition_v1 import AMINO_ACIDS


POSITIVE_FORMAL_CHARGE = frozenset("KR")
NEGATIVE_FORMAL_CHARGE = frozenset("DE")
UNCHARGED_RESIDUES = (
    AMINO_ACIDS - POSITIVE_FORMAL_CHARGE - NEGATIVE_FORMAL_CHARGE)

CHARGE_CLASSES = {
    "positive": POSITIVE_FORMAL_CHARGE,
    "negative": NEGATIVE_FORMAL_CHARGE,
    "uncharged": UNCHARGED_RESIDUES,
}

CHARGE_SIGN = {
    residue: (
        1 if residue in POSITIVE_FORMAL_CHARGE
        else -1 if residue in NEGATIVE_FORMAL_CHARGE
        else 0)
    for residue in AMINO_ACIDS
}


def verify_charge_constitution() -> dict:
    observed = set()
    for name, residues in CHARGE_CLASSES.items():
        overlap = observed & residues
        if overlap:
            raise RuntimeError(
                f"registered charge classes overlap in {name}: "
                f"{''.join(sorted(overlap))}")
        observed.update(residues)
    if observed != AMINO_ACIDS:
        raise RuntimeError("registered charge classes do not close the alphabet")
    if set(CHARGE_SIGN.values()) != {-1, 0, 1}:
        raise RuntimeError("charge-sign relation did not close as negative/zero/positive")
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "classes": {
            name: "".join(sorted(residues))
            for name, residues in CHARGE_CLASSES.items()
        },
        "signs": {
            residue: CHARGE_SIGN[residue] for residue in sorted(AMINO_ACIDS)
        },
    }


CHARGE_CENSUS = verify_charge_constitution()


def dimensionless_electrostatic_relation(
        sequence: str, ca_coordinates: np.ndarray) -> float:
    """Return the generated non-neighbour signed inverse-distance relation."""
    sequence = str(sequence).strip().upper()
    coordinates = np.asarray(ca_coordinates, dtype=float)
    if len(sequence) != len(coordinates):
        raise ValueError("one sequence residue is required per C-alpha coordinate")
    if set(sequence) - AMINO_ACIDS:
        raise ValueError("unsupported residue in charge relation")
    if len(coordinates) < 2:
        return 0.0

    adjacent_d2 = np.sum(np.diff(coordinates, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("charge relation received a degenerate generated step")

    relation = 0.0
    for left in range(len(sequence)):
        left_charge = CHARGE_SIGN[sequence[left]]
        if left_charge == 0:
            continue
        for right in range(left + 2, len(sequence)):
            right_charge = CHARGE_SIGN[sequence[right]]
            if right_charge == 0:
                continue
            distance_d2 = float(np.sum(
                (coordinates[right] - coordinates[left]) ** 2))
            if not math.isfinite(distance_d2) or distance_d2 <= 0:
                raise RuntimeError("charge relation received coincident coordinates")
            relation += (
                left_charge * right_charge
                * math.sqrt(step_d2 / distance_d2)
            )
    if not math.isfinite(relation):
        raise RuntimeError("charge relation produced a non-finite value")
    return relation
