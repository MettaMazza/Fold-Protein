#!/usr/bin/env python3
"""Count explicit side-chain graph contacts in the fold-to-One shell.

The generated adjacent C-alpha step is the endogenous spatial One. Its fold is
the already-constituted hard-exclusion boundary. A non-neighbour atom pair is a
contact exactly when its squared separation is at least the folded step and
less than the complete step. The result is a finite contact-map census over
the explicit covalent side-chain graph points.

No target, template, empirical radius, fitted contact cutoff, learned weight,
reward, energy table, rotamer, or structural database enters this relation.
"""
from __future__ import annotations

import math

import numpy as np

from tools.sidechain_graph_spatial_exclusion_v1 import (
    NON_NEIGHBOUR_SEPARATION, generated_sidechain_graph_points)


CONTACT_SHELL = {
    "inner_boundary": "1/2 fold of generated adjacent C-alpha step",
    "outer_boundary": "one generated adjacent C-alpha step",
    "pair_scope": "explicit atoms on non-neighbour residues",
    "empirical_radius": None,
    "empirical_cutoff": None,
    "fitted_weight": None,
    "reward": None,
    "target": None,
}


def sidechain_graph_contact_relation(sequence: str, atoms) -> dict:
    """Return the exact atom and residue-pair census in the contact shell."""
    sequence = str(sequence).strip().upper()
    graphs = generated_sidechain_graph_points(sequence, atoms)
    contact_pairs = []
    atom_contacts = 0
    for left in sorted(graphs):
        for right in sorted(graphs):
            if right - left < NON_NEIGHBOUR_SEPARATION:
                continue
            left_row, right_row = graphs[left], graphs[right]
            step_d2 = left_row["step_d2"]
            if not math.isfinite(step_d2) or step_d2 <= 0:
                raise RuntimeError("contact relation received a degenerate step")
            fold_d2 = step_d2 / 4
            contacts = []
            for left_atom, left_point in left_row["points"].items():
                for right_atom, right_point in right_row["points"].items():
                    distance_d2 = float(np.sum((right_point - left_point) ** 2))
                    if not math.isfinite(distance_d2):
                        raise RuntimeError("contact separation is non-finite")
                    if fold_d2 <= distance_d2 < step_d2:
                        contacts.append({
                            "left_atom": left_atom,
                            "right_atom": right_atom,
                            "dimensionless_distance_squared": distance_d2 / step_d2,
                        })
            if not contacts:
                continue
            atom_contacts += len(contacts)
            contact_pairs.append({
                "left_residue": left + 1,
                "right_residue": right + 1,
                "left_identity": sequence[left],
                "right_identity": sequence[right],
                "atom_contact_count": len(contacts),
                "contacts": contacts,
            })
    return {
        "contact_residue_pair_count": len(contact_pairs),
        "atom_contact_count": atom_contacts,
        "contact_pairs": contact_pairs,
    }
