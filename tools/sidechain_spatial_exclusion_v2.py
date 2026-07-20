#!/usr/bin/env python3
"""Binary spatial side-chain exclusion with a separate encounter census.

A hard exclusion is the existence of an excluded non-neighbour residue pair.
The exact heavy-atom Cartesian product remains recorded as evidence, but does
not multiply the absolute hard-exclusion stratum. This preserves every v1
generated frame, graph, reach, and separation relation while removing an
implicit graph-cardinality multiplicity from the binary exclusion decision.
"""
from __future__ import annotations

from tools.sidechain_spatial_exclusion_v1 import (
    SIDECHAIN_SPATIAL_EXCLUSION_CENSUS as V1_CENSUS,
    generated_sidechain_command_points,
    sidechain_spatial_exclusion_relation as v1_relation,
    verify_sidechain_spatial_exclusion_constitution)


def verify_binary_sidechain_spatial_exclusion_constitution() -> dict:
    census = dict(verify_sidechain_spatial_exclusion_constitution())
    census.update({
        "hard_exclusion_unit": "one excluded non-neighbour residue pair",
        "encounter_census_role": (
            "recorded exact heavy-atom Cartesian product; not a multiplier "
            "of the binary hard-exclusion stratum"),
    })
    return census


SIDECHAIN_SPATIAL_EXCLUSION_CENSUS = \
    verify_binary_sidechain_spatial_exclusion_constitution()


def sidechain_spatial_exclusion_relation(sequence: str, atoms) -> dict:
    relation = v1_relation(sequence, atoms)
    relation["hard_exclusions"] = relation["excluded_residue_pair_count"]
    return relation

