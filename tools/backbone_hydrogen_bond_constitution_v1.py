#!/usr/bin/env python3
"""Target-incapable backbone hydrogen-bond assembly constitution.

The active blind engine already generates every N, C-alpha, and C position.
Those three atoms determine the peptide-plane frames on both sides of a
backbone hydrogen bond.  This module uses the outward bisectors of those
generated frames as the donor and acceptor directions, normalises separation
by the generated adjacent C-alpha step, and binds donors to acceptors with
unit capacity in strongest-first geometric order.

No O/H coordinates, empirical distance cutoff, angular cutoff, fitted energy,
reward, target, template, rotamer, or learned parameter enters the relation.
Proline is excluded from the donor census because its backbone nitrogen has no
amide hydrogen.  The minimum sequence separation is the already machine-
checked four-residue inter-window count minus its three-residue overlap.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from tools.residue_partition_v1 import AMINO_ACIDS
except ImportError:  # direct execution from tools/
    from residue_partition_v1 import AMINO_ACIDS


INTERWINDOW_RESIDUES = 4
OVERLAP_RESIDUES = 3
MIN_SEQUENCE_SEPARATION = INTERWINDOW_RESIDUES - 1
NON_DONOR_RESIDUES = frozenset("P")
DONOR_RESIDUES = AMINO_ACIDS - NON_DONOR_RESIDUES
ACCEPTOR_RESIDUES = frozenset(AMINO_ACIDS)


def verify_backbone_hydrogen_bond_constitution() -> dict:
    if INTERWINDOW_RESIDUES - OVERLAP_RESIDUES != 1:
        raise RuntimeError("four-residue inter-window overlap did not close")
    if DONOR_RESIDUES | NON_DONOR_RESIDUES != AMINO_ACIDS or \
            DONOR_RESIDUES & NON_DONOR_RESIDUES:
        raise RuntimeError("backbone donor constitution does not close")
    if NON_DONOR_RESIDUES != {"P"}:
        raise RuntimeError("proline must be the unique backbone non-donor")
    if ACCEPTOR_RESIDUES != AMINO_ACIDS:
        raise RuntimeError("backbone acceptor constitution does not close")
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "donor_residues": "".join(sorted(DONOR_RESIDUES)),
        "non_donor_residues": "P",
        "acceptor_residues": "".join(sorted(ACCEPTOR_RESIDUES)),
        "interwindow_residues": INTERWINDOW_RESIDUES,
        "overlap_residues": OVERLAP_RESIDUES,
        "minimum_sequence_separation": MIN_SEQUENCE_SEPARATION,
        "donor_capacity": 1,
        "acceptor_capacity": 1,
        "distance_cutoff": None,
        "angular_cutoff": None,
        "fitted_energy": None,
    }


HYDROGEN_BOND_CENSUS = verify_backbone_hydrogen_bond_constitution()


def _unit(vector: np.ndarray) -> np.ndarray:
    length = float(np.linalg.norm(vector))
    if not math.isfinite(length) or length <= 0:
        raise RuntimeError("hydrogen-bond relation received a degenerate frame")
    return vector / length


def _residue_backbone(sequence: str, atoms) -> list[dict[str, np.ndarray]]:
    sequence = str(sequence).strip().upper()
    if not sequence or set(sequence) - AMINO_ACIDS:
        raise ValueError("hydrogen-bond relation requires a supported sequence")
    by_resnum = {}
    for atom in atoms:
        name = atom.get("name")
        if name not in {"N", "CA", "C"}:
            continue
        resnum = int(atom.get("resnum", 0))
        row = by_resnum.setdefault(resnum, {})
        if resnum < 1 or name in row:
            raise RuntimeError("generated backbone atom identity does not close")
        row[name] = np.asarray(atom["coord"], dtype=float)
    ordered_resnums = sorted(by_resnum)
    if len(ordered_resnums) != len(sequence):
        raise RuntimeError("generated backbone residue census does not close")
    rows = [by_resnum[resnum] for resnum in ordered_resnums]
    for index, row in enumerate(rows):
        if set(row) != {"N", "CA", "C"}:
            raise RuntimeError(
                f"generated residue {index + 1} lacks a complete N/CA/C frame")
    return rows


def backbone_hydrogen_bond_relation(sequence: str, atoms) -> dict:
    """Return deterministic unit-capacity donor/acceptor assembly evidence."""
    sequence = str(sequence).strip().upper()
    rows = _residue_backbone(sequence, atoms)
    if len(rows) < INTERWINDOW_RESIDUES:
        return {
            "relation": 0.0,
            "pair_count": 0,
            "eligible_pair_count": 0,
            "pairs": [],
        }

    ca = np.asarray([row["CA"] for row in rows], dtype=float)
    adjacent_d2 = np.sum(np.diff(ca, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("hydrogen-bond relation received a degenerate step")

    donor_directions = {}
    for donor in range(1, len(rows)):
        if sequence[donor] not in DONOR_RESIDUES:
            continue
        nitrogen = rows[donor]["N"]
        to_previous_carbon = _unit(rows[donor - 1]["C"] - nitrogen)
        to_alpha_carbon = _unit(rows[donor]["CA"] - nitrogen)
        donor_directions[donor] = _unit(
            -(to_previous_carbon + to_alpha_carbon))

    acceptor_directions = {}
    for acceptor in range(len(rows) - 1):
        carbon = rows[acceptor]["C"]
        to_alpha_carbon = _unit(rows[acceptor]["CA"] - carbon)
        to_next_nitrogen = _unit(rows[acceptor + 1]["N"] - carbon)
        acceptor_directions[acceptor] = _unit(
            -(to_alpha_carbon + to_next_nitrogen))

    eligible = []
    for donor, donor_direction in donor_directions.items():
        nitrogen = rows[donor]["N"]
        for acceptor, acceptor_direction in acceptor_directions.items():
            if abs(donor - acceptor) < MIN_SEQUENCE_SEPARATION:
                continue
            carbon = rows[acceptor]["C"]
            donor_to_acceptor = _unit(carbon - nitrogen)
            acceptor_to_donor = -donor_to_acceptor
            donor_alignment = max(
                0.0, float(np.dot(donor_direction, donor_to_acceptor)))
            acceptor_alignment = max(
                0.0, float(np.dot(
                    acceptor_direction, acceptor_to_donor)))
            distance_d2 = float(np.sum((carbon - nitrogen) ** 2))
            if not math.isfinite(distance_d2) or distance_d2 <= 0:
                raise RuntimeError(
                    "hydrogen-bond relation received coincident frames")
            strength = (
                donor_alignment * acceptor_alignment
                * math.sqrt(step_d2 / distance_d2)
            )
            if strength > 0:
                eligible.append((strength, donor, acceptor))

    eligible.sort(key=lambda row: (-row[0], row[1], row[2]))
    held_donors = set()
    held_acceptors = set()
    pairs = []
    for strength, donor, acceptor in eligible:
        if donor in held_donors or acceptor in held_acceptors:
            continue
        held_donors.add(donor)
        held_acceptors.add(acceptor)
        pairs.append({
            "donor_residue": donor + 1,
            "acceptor_residue": acceptor + 1,
            "dimensionless_strength": strength,
        })
    total = sum(row["dimensionless_strength"] for row in pairs)
    if not math.isfinite(total):
        raise RuntimeError("hydrogen-bond relation is non-finite")
    return {
        "relation": -total,
        "pair_count": len(pairs),
        "eligible_pair_count": len(eligible),
        "pairs": pairs,
    }


def dimensionless_backbone_hydrogen_bond_relation(
        sequence: str, atoms) -> float:
    """Return the minimised negative unit-capacity pairing strength."""
    return float(backbone_hydrogen_bond_relation(sequence, atoms)["relation"])
