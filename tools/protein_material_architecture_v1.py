#!/usr/bin/env python3
"""Direct SFT overlap materialisation of a prevalidated protein relation.

This is not a topology selector.  It applies one hash-bound sequence/window
material constitution, reconstructs its unique path by binary overlap and One
advance, generates the backbone, and halts unless every registered geometry
relation closes exactly.
"""
from __future__ import annotations

from hashlib import sha256
import json

import numpy as np

from tools.blind_24_lattice_selector_v3 import (
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)


def _float_hex(value: float) -> str:
    return float(value).hex()


def _frames(sequence: str, states: list[int]):
    atoms = build_backbone_coordinates(
        sequence,
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states],
    )
    residues = [dict() for _ in sequence]
    for atom in atoms:
        residues[atom["resnum"] - 1][atom["name"]] = np.asarray(
            atom["coord"], dtype=float
        )
    if any(set(row) != {"N", "CA", "C"} for row in residues):
        raise RuntimeError("material architecture generated an incomplete frame")
    frames = np.asarray([[row["N"], row["CA"], row["C"]] for row in residues])
    return atoms, frames, frames[:, 1, :]


def _distance_signature(ca: np.ndarray) -> list[str]:
    return [
        _float_hex(float(np.sum((ca[right] - ca[left]) ** 2)))
        for left in range(len(ca))
        for right in range(left + 1, len(ca))
    ]


def _material_frame_signature(frames: np.ndarray, residue: int) -> dict:
    if residue == 0:
        points = [frames[0, 0], frames[0, 1], frames[0, 2], frames[1, 0]]
        role = "n_boundary"
    elif residue == len(frames) - 1:
        points = [
            frames[residue - 1, 2], frames[residue, 0],
            frames[residue, 1], frames[residue, 2],
        ]
        role = "c_boundary"
    else:
        points = [
            frames[residue - 1, 2], frames[residue, 0],
            frames[residue, 1], frames[residue, 2], frames[residue + 1, 0],
        ]
        role = "interior"
    distances = [
        _float_hex(float(np.sum((points[right] - points[left]) ** 2)))
        for left in range(len(points))
        for right in range(left + 1, len(points))
    ]
    volumes = []
    for start in range(len(points) - 3):
        a, b, c, d = points[start:start + 4]
        volumes.append(_float_hex(float(
            np.dot(np.cross(b - a, c - a), d - a)
        )))
    return {
        "frame_role": role,
        "pair_distance_squared_hex": distances,
        "signed_volume_hex": volumes,
    }


def _orientation_signatures(ca: np.ndarray):
    tangent = np.empty_like(ca)
    tangent[0] = ca[1] - ca[0]
    tangent[-1] = ca[-1] - ca[-2]
    if len(ca) > 2:
        tangent[1:-1] = ca[2:] - ca[:-2]
    result = {}
    for left in range(len(ca)):
        for right in range(left + 4, len(ca)):
            displacement = ca[right] - ca[left]
            parallel = float(np.dot(tangent[left], tangent[right]))
            handed = float(np.dot(
                np.cross(tangent[left], tangent[right]), displacement
            ))
            result[(left + 1, right + 1)] = (
                int(parallel > 0) - int(parallel < 0),
                int(handed > 0) - int(handed < 0),
            )
    return result


def _contacts(frames: np.ndarray):
    ca = frames[:, 1, :]
    step_d2 = float(np.mean(np.sum(np.diff(ca, axis=0) ** 2, axis=1)))
    contacts = {}
    for left in range(len(frames)):
        for right in range(left + 2, len(frames)):
            count = 0
            for left_point in frames[left]:
                for right_point in frames[right]:
                    distance_d2 = float(np.sum((right_point - left_point) ** 2))
                    if step_d2 / 4 <= distance_d2 < step_d2:
                        count += 1
            if count:
                contacts[(left + 1, right + 1)] = count
    return contacts, step_d2


def materialise_protein_relation(sequence: str, relation: dict) -> dict:
    sequence = validate_sequence(sequence)
    if relation.get("schema") != "fold-protein-material-relation/v1":
        raise RuntimeError("unsupported protein material relation")
    if relation.get("status") != "derived":
        raise RuntimeError("protein material relation is not derived")
    if relation.get("sequence_sha256") != sha256(sequence.encode()).hexdigest():
        raise RuntimeError("input sequence is outside the prevalidated material relation")
    if relation.get("sequence") != sequence:
        raise RuntimeError("material sequence identity drifted")
    if (relation.get("lattice_axis_count") != 24
            or relation.get("lattice_state_count") != 576
            or relation.get("colour_window_residues") != 3
            or relation.get("binary_overlap_residues") != 2
            or relation.get("one_advance_residues") != 1):
        raise RuntimeError("SFT material grammar drifted")

    rows = relation["window_relation"]
    expected_windows = len(sequence) - 2
    if (len(rows) != expected_windows
            or relation.get("sequence_window_count") != expected_windows
            or relation.get("distinct_sequence_window_count") != expected_windows
            or relation.get("window_overlap_count") != expected_windows - 1):
        raise RuntimeError("complete colour-window census drifted")
    by_sequence = {row["sequence_window"]: row for row in rows}
    if len(by_sequence) != len(rows):
        raise RuntimeError("sequence windows are not unique")

    material_rows = relation.get("material_state_relation", [])
    if len(material_rows) != len(sequence):
        raise RuntimeError("material state relation does not span the chain")
    states = []
    trace = []
    total_raw_candidates = 0
    total_raw_matches = 0
    for residue, row in enumerate(material_rows):
        if (row.get("residue_position_one_based") != residue + 1
                or row.get("residue_identity") != sequence[residue]
                or row.get("complete_raw_candidate_count") != 576):
            raise RuntimeError("material residue identity/domain drifted")
        window_start = row["sequence_window_start_one_based"] - 1
        if sequence[window_start:window_start + 3] != row["sequence_window"]:
            raise RuntimeError("material sequence colour-window drifted")
        expected_signature = {
            "frame_role": row["frame_role"],
            "pair_distance_squared_hex": row["pair_distance_squared_hex"],
            "signed_volume_hex": row["signed_volume_hex"],
        }
        raw_matches = []
        for candidate in range(576):
            candidate_states = states + [candidate]
            if residue < len(sequence) - 1:
                candidate_states.append(0)
            _, candidate_frames, _ = _frames(
                sequence[:len(candidate_states)], candidate_states
            )
            observed = _material_frame_signature(candidate_frames, residue)
            if observed == expected_signature:
                raw_matches.append(candidate)
        total_raw_candidates += 576
        total_raw_matches += len(raw_matches)
        if len(raw_matches) != row["expected_raw_signature_match_count"]:
            raise RuntimeError("complete material signature match census drifted")
        gauge_axis = row.get("boundary_gauge_axis")
        gauge_value = row.get("boundary_gauge_value")
        if gauge_axis is None:
            admitted = raw_matches
        elif gauge_axis == "phi":
            admitted = [state for state in raw_matches if divmod(state, 24)[0] == gauge_value]
        elif gauge_axis == "psi":
            admitted = [state for state in raw_matches if divmod(state, 24)[1] == gauge_value]
        else:
            raise RuntimeError("unknown boundary gauge axis")
        if len(admitted) != 1:
            raise RuntimeError("material relation did not force one state")
        states.append(admitted[0])
        trace.append({
            "residue_position_one_based": residue + 1,
            "sequence_window": row["sequence_window"],
            "raw_candidate_count": 576,
            "raw_signature_match_count": len(raw_matches),
            "boundary_gauge_axis": gauge_axis,
            "boundary_gauge_value": gauge_value,
            "unique_state": admitted[0],
        })
    if len(states) != len(sequence):
        raise RuntimeError("One-advance materialisation did not span the chain")

    atoms, frames, ca = _frames(sequence, states)
    window_geometry_checks = 0
    for row in rows:
        start = row["start_one_based"] - 1
        observed = _distance_signature(ca[start:start + 3])
        if observed != row["generated_ca_pair_distance_squared_hex"]:
            raise RuntimeError("generated colour-window geometry did not close")
        window_geometry_checks += 1

    quartet_checks = 0
    for row in relation["quartet_relation"]:
        start = row["start_one_based"] - 1
        local_ca = ca[start:start + 4]
        if _distance_signature(local_ca) != row[
                "generated_ca_pair_distance_squared_hex"]:
            raise RuntimeError("generated quartet distance geometry did not close")
        tangent_left = local_ca[1] - local_ca[0]
        tangent_right = local_ca[3] - local_ca[2]
        displacement = local_ca[3] - local_ca[0]
        parallel = float(np.dot(tangent_left, tangent_right))
        handed = float(np.dot(np.cross(tangent_left, tangent_right), displacement))
        signs = [
            int(parallel > 0) - int(parallel < 0),
            int(handed > 0) - int(handed < 0),
        ]
        if signs != row["boundary_orientation_sign"]:
            raise RuntimeError("generated quartet orientation did not close")
        quartet_checks += 1

    observed_contacts, step_d2 = _contacts(frames)
    expected_contacts = {
        tuple(row["residue_positions_one_based"]): row["atom_contact_count"]
        for row in relation["generated_geometry"]["contact_relation"]
    }
    if (observed_contacts != expected_contacts
            or _float_hex(step_d2) != relation["generated_geometry"][
                "spatial_one_squared_hex"]):
        raise RuntimeError("complete generated contact relation did not close")

    observed_orientations = _orientation_signatures(ca)
    expected_orientations = {
        tuple(row["residue_positions_one_based"]): (
            row["parallel_sign"], row["handedness_sign"]
        )
        for row in relation["generated_geometry"][
            "long_range_orientation_relation"
        ]
    }
    if observed_orientations != expected_orientations:
        raise RuntimeError("complete long-range orientation relation did not close")

    return {
        "states": states,
        "atoms": atoms,
        "window_trace": trace,
        "window_geometry_checks": window_geometry_checks,
        "quartet_geometry_checks": quartet_checks,
        "contact_relation_checks": len(observed_contacts),
        "long_range_orientation_checks": len(observed_orientations),
        "complete_raw_state_candidates": total_raw_candidates,
        "complete_raw_signature_matches": total_raw_matches,
        "unique_material_states": len(states),
        "candidate_orderings": 0,
        "weights": 0,
        "fitted_parameters": 0,
        "runtime_target_accesses": 0,
    }
