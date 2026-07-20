#!/usr/bin/env python3
"""Target-incapable spatial side-chain exclusion from generated backbone frames.

Every non-glycine residue receives an oriented side-chain command point in the
L-amino-acid half-space of its generated N/CA/C frame. The exact heavy-atom
graph census supplies a fold share n/(n+1) of the generated adjacent C-alpha
step, so larger constituted graphs extend farther without an empirical radius.
Two non-neighbour side-chain commands are excluded when their generated points
are closer than that same endogenous adjacent step. The integer exclusion
census is the Cartesian-product count of their constituted heavy atoms.

No target, template, rotamer, empirical bond angle, residue radius, fitted
weight, learned parameter, reward, or imported distance table enters.
"""
from __future__ import annotations

import math

import numpy as np

from tools.backbone_hydrogen_bond_constitution_v1 import _residue_backbone
from tools.residue_partition_v1 import AMINO_ACIDS
from tools.residue_steric_constitution_v1 import (
    SIDECHAIN_HEAVY_ATOM_COUNT, STERIC_CENSUS)


GLYCINE = "G"
NON_NEIGHBOUR_SEPARATION = 2


def verify_sidechain_spatial_exclusion_constitution() -> dict:
    if set(SIDECHAIN_HEAVY_ATOM_COUNT) != AMINO_ACIDS:
        raise RuntimeError("side-chain spatial alphabet does not close")
    if SIDECHAIN_HEAVY_ATOM_COUNT[GLYCINE] != 0:
        raise RuntimeError("glycine did not close as the empty spatial graph")
    if NON_NEIGHBOUR_SEPARATION != 2:
        raise RuntimeError("non-neighbour separation drifted")
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "glycine_sidechain_atoms": 0,
        "chirality": "L positive cross(CA-to-N, CA-to-C) half-space",
        "reach": "sidechain_heavy_atom_count / (count + 1) of generated adjacent C-alpha step",
        "non_neighbour_sequence_separation": NON_NEIGHBOUR_SEPARATION,
        "exclusion_unit": "generated mean adjacent C-alpha squared step",
        "encounter_census": "Cartesian product of exact side-chain heavy-atom graph counts",
        "empirical_residue_radius": None,
        "empirical_distance_cutoff": None,
        "rotamer": None,
        "fitted_weight": None,
        "reward": None,
        "target": None,
        "steric_census": STERIC_CENSUS,
    }


SIDECHAIN_SPATIAL_EXCLUSION_CENSUS = \
    verify_sidechain_spatial_exclusion_constitution()


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm <= 0:
        raise RuntimeError("side-chain spatial frame is degenerate")
    return np.asarray(vector, dtype=float) / norm


def generated_sidechain_command_points(sequence: str, atoms) -> dict[int, dict]:
    sequence = str(sequence).strip().upper()
    if set(sequence) - AMINO_ACIDS:
        raise ValueError("unsupported residue in side-chain spatial relation")
    rows = _residue_backbone(sequence, atoms)
    if len(rows) != len(sequence):
        raise RuntimeError("one generated backbone frame is required per residue")
    if len(rows) < 2:
        return {}

    ca = np.asarray([row["CA"] for row in rows], dtype=float)
    adjacent_d2 = np.sum(np.diff(ca, axis=0) ** 2, axis=1)
    step_d2 = float(np.mean(adjacent_d2))
    if not math.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("side-chain spatial relation received a degenerate step")
    step = math.sqrt(step_d2)

    commands = {}
    for index, (residue, row) in enumerate(zip(sequence, rows)):
        count = SIDECHAIN_HEAVY_ATOM_COUNT[residue]
        if count == 0:
            continue
        ca_to_n = row["N"] - row["CA"]
        ca_to_c = row["C"] - row["CA"]
        direction = _unit(np.cross(ca_to_n, ca_to_c))
        reach_share = count / (count + 1)
        commands[index] = {
            "residue": residue,
            "heavy_atom_count": count,
            "reach_share": reach_share,
            "direction": direction,
            "point": row["CA"] + direction * (step * reach_share),
            "step_d2": step_d2,
        }
    return commands


def sidechain_spatial_exclusion_relation(sequence: str, atoms) -> dict:
    sequence = str(sequence).strip().upper()
    commands = generated_sidechain_command_points(sequence, atoms)
    if not commands:
        return {
            "hard_exclusions": 0,
            "excluded_residue_pair_count": 0,
            "possible_heavy_atom_encounters": 0,
            "excluded_pairs": [],
        }
    step_d2 = next(iter(commands.values()))["step_d2"]
    excluded_pairs = []
    hard_exclusions = 0
    for left in sorted(commands):
        for right in sorted(commands):
            if right - left < NON_NEIGHBOUR_SEPARATION:
                continue
            left_row, right_row = commands[left], commands[right]
            distance_d2 = float(np.sum(
                (right_row["point"] - left_row["point"]) ** 2))
            if not math.isfinite(distance_d2):
                raise RuntimeError("side-chain spatial separation is non-finite")
            if distance_d2 >= step_d2:
                continue
            encounters = (
                left_row["heavy_atom_count"]
                * right_row["heavy_atom_count"])
            hard_exclusions += encounters
            excluded_pairs.append({
                "left_residue": left + 1,
                "right_residue": right + 1,
                "left_identity": sequence[left],
                "right_identity": sequence[right],
                "possible_heavy_atom_encounters": encounters,
                "dimensionless_command_distance_squared":
                    distance_d2 / step_d2,
            })
    return {
        "hard_exclusions": hard_exclusions,
        "excluded_residue_pair_count": len(excluded_pairs),
        "possible_heavy_atom_encounters": hard_exclusions,
        "excluded_pairs": excluded_pairs,
    }
