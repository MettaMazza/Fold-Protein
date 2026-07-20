#!/usr/bin/env python3
"""Exact complement of the fold-to-One explicit atom contact map.

For a fixed sequence prefix, every Cartesian atom pair on non-neighbour
side-chain graphs is generated before geometry is selected. V1 counts which
pairs occupy the contact shell. V2 takes the exact finite complement: possible
atom pairs minus occupied contacts. This supplies a non-negative integer
contact-deficit stratum without a fitted target contact count or scalar weight.
"""
from __future__ import annotations

from tools.sidechain_graph_contact_topology_v1 import (
    CONTACT_SHELL, sidechain_graph_contact_relation)
from tools.sidechain_graph_spatial_exclusion_v1 import (
    NON_NEIGHBOUR_SEPARATION, generated_sidechain_graph_points)


CONTACT_DEFICIT_CENSUS = {
    **CONTACT_SHELL,
    "deficit": "possible explicit atom pairs minus fold-to-One atom contacts",
    "target_contact_count": None,
}


def sidechain_graph_contact_deficit_relation(sequence: str, atoms) -> dict:
    sequence = str(sequence).strip().upper()
    graphs = generated_sidechain_graph_points(sequence, atoms)
    possible = 0
    for left in sorted(graphs):
        for right in sorted(graphs):
            if right - left < NON_NEIGHBOUR_SEPARATION:
                continue
            possible += len(graphs[left]["points"]) * len(graphs[right]["points"])
    contact = sidechain_graph_contact_relation(sequence, atoms)
    occupied = int(contact["atom_contact_count"])
    deficit = possible - occupied
    if deficit < 0:
        raise RuntimeError("contact deficit did not close as a finite complement")
    return {
        **contact,
        "possible_atom_pair_count": possible,
        "contact_deficit": deficit,
    }
