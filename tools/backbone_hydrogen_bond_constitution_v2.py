#!/usr/bin/env python3
"""Topology-separated target-incapable backbone hydrogen-bond constitution.

V2 preserves the generated N/CA/C frames, endogenous step normalization and
global unit-capacity assembly of v1.  It replaces the undifferentiated minimum
sequence separation with two generated topology classes:

* alpha: the donor is exactly four residues after its acceptor (i+4 -> i);
* inter-strand: donor and acceptor are separated by more than four residues.

The four-residue relation is the already machine-checked inter-window count.
"Longer" is its strict complement among non-local pairs.  The two assembled
strengths are exposed independently so the symmetric ordinal selector does not
blend them with an agent-authored weight.  One global strongest-first matching
retains one bond capacity for every donor and acceptor across both classes.

No target, template, empirical cutoff, fitted energy, learned parameter or
continuous tuning constant enters this relation.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from tools.backbone_hydrogen_bond_constitution_v1 import (
        ACCEPTOR_RESIDUES, DONOR_RESIDUES, INTERWINDOW_RESIDUES,
        NON_DONOR_RESIDUES, _residue_backbone, _unit)
    from tools.residue_partition_v1 import AMINO_ACIDS
except ImportError:  # direct execution from tools/
    from backbone_hydrogen_bond_constitution_v1 import (
        ACCEPTOR_RESIDUES, DONOR_RESIDUES, INTERWINDOW_RESIDUES,
        NON_DONOR_RESIDUES, _residue_backbone, _unit)
    from residue_partition_v1 import AMINO_ACIDS


ALPHA_SEQUENCE_SEPARATION = INTERWINDOW_RESIDUES
INTERSTRAND_MINIMUM_SEPARATION = INTERWINDOW_RESIDUES + 1
TOPOLOGY_CLASSES = ("alpha", "interstrand")


def verify_topology_hydrogen_bond_constitution() -> dict:
    if INTERWINDOW_RESIDUES != 4:
        raise RuntimeError("machine-checked inter-window count drifted")
    if ALPHA_SEQUENCE_SEPARATION != INTERWINDOW_RESIDUES:
        raise RuntimeError("alpha topology did not close to four residues")
    if INTERSTRAND_MINIMUM_SEPARATION != INTERWINDOW_RESIDUES + 1:
        raise RuntimeError("longer inter-strand topology did not close")
    if DONOR_RESIDUES | NON_DONOR_RESIDUES != AMINO_ACIDS or \
            DONOR_RESIDUES & NON_DONOR_RESIDUES:
        raise RuntimeError("backbone donor constitution does not close")
    if ACCEPTOR_RESIDUES != AMINO_ACIDS:
        raise RuntimeError("backbone acceptor constitution does not close")
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "donor_residues": "".join(sorted(DONOR_RESIDUES)),
        "non_donor_residues": "P",
        "acceptor_residues": "".join(sorted(ACCEPTOR_RESIDUES)),
        "interwindow_residues": INTERWINDOW_RESIDUES,
        "alpha_sequence_separation": ALPHA_SEQUENCE_SEPARATION,
        "interstrand_minimum_separation": INTERSTRAND_MINIMUM_SEPARATION,
        "topology_classes": list(TOPOLOGY_CLASSES),
        "global_donor_capacity": 1,
        "global_acceptor_capacity": 1,
        "distance_cutoff": None,
        "angular_cutoff": None,
        "fitted_energy": None,
        "topology_weight": None,
    }


TOPOLOGY_HYDROGEN_BOND_CENSUS = \
    verify_topology_hydrogen_bond_constitution()


def _topology(donor: int, acceptor: int) -> str | None:
    if donor - acceptor == ALPHA_SEQUENCE_SEPARATION:
        return "alpha"
    if abs(donor - acceptor) >= INTERSTRAND_MINIMUM_SEPARATION:
        return "interstrand"
    return None


def topology_backbone_hydrogen_bond_relation(sequence: str, atoms) -> dict:
    """Return one global matching with separate alpha/inter-strand evidence."""
    sequence = str(sequence).strip().upper()
    rows = _residue_backbone(sequence, atoms)
    empty = {
        "relations": {"alpha": 0.0, "interstrand": 0.0},
        "pair_count": 0,
        "pair_counts": {"alpha": 0, "interstrand": 0},
        "eligible_pair_count": 0,
        "eligible_pair_counts": {"alpha": 0, "interstrand": 0},
        "pairs": [],
    }
    if len(rows) <= INTERWINDOW_RESIDUES:
        return empty

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
        donor_directions[donor] = _unit(-(
            _unit(rows[donor - 1]["C"] - nitrogen)
            + _unit(rows[donor]["CA"] - nitrogen)))

    acceptor_directions = {}
    for acceptor in range(len(rows) - 1):
        carbon = rows[acceptor]["C"]
        acceptor_directions[acceptor] = _unit(-(
            _unit(rows[acceptor]["CA"] - carbon)
            + _unit(rows[acceptor + 1]["N"] - carbon)))

    eligible = []
    eligible_counts = {name: 0 for name in TOPOLOGY_CLASSES}
    for donor, donor_direction in donor_directions.items():
        nitrogen = rows[donor]["N"]
        for acceptor, acceptor_direction in acceptor_directions.items():
            topology = _topology(donor, acceptor)
            if topology is None:
                continue
            carbon = rows[acceptor]["C"]
            donor_to_acceptor = _unit(carbon - nitrogen)
            donor_alignment = max(
                0.0, float(np.dot(donor_direction, donor_to_acceptor)))
            acceptor_alignment = max(
                0.0, float(np.dot(acceptor_direction, -donor_to_acceptor)))
            distance_d2 = float(np.sum((carbon - nitrogen) ** 2))
            if not math.isfinite(distance_d2) or distance_d2 <= 0:
                raise RuntimeError(
                    "hydrogen-bond relation received coincident frames")
            strength = (donor_alignment * acceptor_alignment
                        * math.sqrt(step_d2 / distance_d2))
            if strength > 0:
                eligible.append((strength, donor, acceptor, topology))
                eligible_counts[topology] += 1

    eligible.sort(key=lambda row: (-row[0], row[1], row[2], row[3]))
    held_donors = set()
    held_acceptors = set()
    pairs = []
    totals = {name: 0.0 for name in TOPOLOGY_CLASSES}
    pair_counts = {name: 0 for name in TOPOLOGY_CLASSES}
    for strength, donor, acceptor, topology in eligible:
        if donor in held_donors or acceptor in held_acceptors:
            continue
        held_donors.add(donor)
        held_acceptors.add(acceptor)
        totals[topology] += strength
        pair_counts[topology] += 1
        pairs.append({
            "topology": topology,
            "donor_residue": donor + 1,
            "acceptor_residue": acceptor + 1,
            "sequence_separation": abs(donor - acceptor),
            "dimensionless_strength": strength,
        })
    if not all(math.isfinite(value) for value in totals.values()):
        raise RuntimeError("hydrogen-bond relation is non-finite")
    return {
        "relations": {name: -totals[name] for name in TOPOLOGY_CLASSES},
        "pair_count": len(pairs),
        "pair_counts": pair_counts,
        "eligible_pair_count": len(eligible),
        "eligible_pair_counts": eligible_counts,
        "pairs": pairs,
    }


def dimensionless_topology_hydrogen_bond_relations(
        sequence: str, atoms) -> tuple[float, float]:
    relation = topology_backbone_hydrogen_bond_relation(sequence, atoms)
    return tuple(float(relation["relations"][name])
                 for name in TOPOLOGY_CLASSES)
