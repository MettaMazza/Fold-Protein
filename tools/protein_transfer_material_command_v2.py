#!/usr/bin/env python3
"""Transferable sequence-only material command for Material Architecture V1.

The command is an observationally derived transparent law.  Runtime receives
only an amino-acid sequence and a frozen command.  It derives one 24x24 state
per residue from constituted residue material and SFT binary/colour/One
addresses, then emits the exact material relation consumed by the unchanged
complete-domain Material Architecture V1 census.
"""
from __future__ import annotations

import ast
from hashlib import sha256
import json

import numpy as np

from tools.analyze_transferable_material_grammar_v1 import (
    AXIS, BINARY, COLOUR, ONE, generated_grammar, mod_vector,
    residue_material, shifted,
)
from tools.protein_material_architecture_v1 import (
    _contacts, _distance_signature, _frames, _material_frame_signature,
    _orientation_signatures,
)
from tools.analyze_transferable_global_material_grammar_v2 import (
    BLOCK_SCALES, preceding_block, prefix, suffix,
)
from tools.blind_24_lattice_selector_v3 import validate_sequence


MATERIAL_FIELDS = ("atom", "bond", "branch", "cycle", "charge", "packing", "donor")


def sequence_primitives(sequence: str) -> dict[str, tuple[int, ...]]:
    """Generate the complete registered sequence-only SFT address basis."""
    sequence = validate_sequence(sequence)
    material = residue_material(sequence)
    count = len(sequence)
    values: dict[str, tuple[int, ...]] = {}
    for name, vector in material.items():
        for offset, label in ((-ONE, "left"), (0, "self"), (ONE, "right")):
            values[f"{label}_{name}"] = mod_vector(shifted(vector, offset))
        left = shifted(vector, -ONE)
        right = shifted(vector, ONE)
        values[f"window_{name}"] = mod_vector(
            left[index] + vector[index] + right[index]
            for index in range(count)
        )
        values[f"advance_{name}"] = mod_vector(
            right[index] - left[index] for index in range(count)
        )

    position = tuple(range(ONE, count + ONE))
    values["one"] = (ONE,) * count
    values["binary"] = (BINARY,) * count
    values["colour"] = (COLOUR,) * count
    values["reverse_position"] = mod_vector(count + ONE - value for value in position)
    values["chain_count"] = (count % AXIS,) * count
    for name, vector in material.items():
        before = prefix(vector)
        after = suffix(vector)
        values[f"prefix_{name}"] = mod_vector(before)
        values[f"suffix_{name}"] = mod_vector(after)
        values[f"material_complement_{name}"] = mod_vector(
            after[index] - before[index] for index in range(count)
        )
        for size in BLOCK_SCALES:
            values[f"block_{size}_{name}"] = mod_vector(
                preceding_block(vector, size)
            )
            values[f"block_address_{size}_{name}"] = mod_vector(
                sum(vector[max(0, index - size + ONE):index + ONE])
                + (index // size)
                for index in range(count)
            )
    return values


def constitution_signatures(sequence: str) -> list[tuple[int, ...]]:
    material = residue_material(sequence)
    return [
        tuple(material[field][index] for field in MATERIAL_FIELDS)
        for index in range(len(sequence))
    ]


def _vector_binary(left: tuple[int, ...], right: tuple[int, ...], operation):
    return tuple(operation(a, b) % AXIS for a, b in zip(left, right))


def evaluate_expression(expression: str, primitives: dict[str, tuple[int, ...]]):
    """Evaluate only the closed expression language emitted by the grammar."""
    tree = ast.parse(expression.replace("One", "one"), mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Name):
            if node.id not in primitives:
                raise RuntimeError(f"material command primitive unavailable: {node.id}")
            return primitives[node.id]
        if isinstance(node, ast.BinOp):
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return _vector_binary(left, right, lambda a, b: a + b)
            if isinstance(node.op, ast.Sub):
                return _vector_binary(left, right, lambda a, b: a - b)
            if isinstance(node.op, ast.Mult):
                return _vector_binary(left, right, lambda a, b: a * b)
            raise RuntimeError("material command contains an unsupported binary form")
        if isinstance(node, ast.Call) and len(node.args) == 1 and not node.keywords:
            value = evaluate(node.args[0])
            if isinstance(node.func, ast.Name) and node.func.id == "fold":
                return tuple((BINARY * item) % AXIS for item in value)
            if isinstance(node.func, ast.Name) and node.func.id == "antipode":
                return tuple((-item) % AXIS for item in value)
        raise RuntimeError("material command expression left the admitted grammar")

    return evaluate(tree.body)


def material_state_path(sequence: str, command: dict) -> dict:
    sequence = validate_sequence(sequence)
    if (command.get("schema") != "fold-protein-transfer-material-command/v2"
            or command.get("status") != "derived"
            or command.get("axis_modulus") != AXIS
            or command.get("colour_window") != COLOUR
            or command.get("binary_overlap") != BINARY
            or command.get("one_advance") != ONE):
        raise RuntimeError("transfer material command is not admitted")
    primitives = sequence_primitives(sequence)
    signatures = constitution_signatures(sequence)
    expression_cache = {}
    axes = {}
    trace = []
    for axis_name in ("phi", "psi"):
        rows = command["axis_commands"][axis_name]
        values = []
        for index, signature in enumerate(signatures):
            matches = [
                row for row in rows
                if tuple(row["material_signature"]) == signature
                and (row["colour_position"] is None
                     or row["colour_position"] == index % COLOUR)
            ]
            if len(matches) != 1:
                raise RuntimeError(
                    f"material command has {len(matches)} matches for "
                    f"{axis_name} residue {index + 1} signature={signature} "
                    f"colour={index % COLOUR}")
            row = matches[0]
            pair_values = []
            for expression in row["expression_pair"]:
                if expression not in expression_cache:
                    expression_cache[expression] = evaluate_expression(
                        expression, primitives)
                pair_values.append(expression_cache[expression][index])
            raw_value = sum(pair_values) % AXIS
            boundary_gauge = (
                axis_name == "phi" and index == 0
            ) or (
                axis_name == "psi" and index == len(sequence) - 1
            )
            values.append(0 if boundary_gauge else raw_value)
            trace.append({
                "axis": axis_name,
                "residue_position_one_based": index + 1,
                "material_signature": list(signature),
                "colour_position": index % COLOUR,
                "command_scope": row["scope"],
                "expression_pair": row["expression_pair"],
                "pre_gauge_axis_value": raw_value,
                "canonical_boundary_gauge": boundary_gauge,
                "axis_value": values[-1],
            })
        axes[axis_name] = values
    states = [
        axes["phi"][index] * AXIS + axes["psi"][index]
        for index in range(len(sequence))
    ]
    return {
        "states": states,
        "phi_axis": axes["phi"],
        "psi_axis": axes["psi"],
        "command_trace": trace,
        "candidate_orderings": 0,
        "weights": 0,
        "fitted_parameters": 0,
        "runtime_target_accesses": 0,
    }


def relation_from_command(sequence: str, command: dict) -> dict:
    """Build the exact V1 material relation from the sequence-only command."""
    material = material_state_path(sequence, command)
    states = material["states"]
    atoms, frames, ca = _frames(sequence, states)
    windows = []
    for start in range(len(sequence) - 2):
        windows.append({
            "start_one_based": start + 1,
            "sequence_window": sequence[start:start + 3],
            "generated_ca_pair_distance_squared_hex": _distance_signature(
                ca[start:start + 3]
            ),
        })
    if len({row["sequence_window"] for row in windows}) != len(windows):
        raise RuntimeError("transfer sequence has repeated colour windows")

    quartets = []
    for start in range(len(sequence) - 3):
        local = ca[start:start + 4]
        left = local[1] - local[0]
        right = local[3] - local[2]
        displacement = local[3] - local[0]
        parallel = float(np.dot(left, right))
        handed = float(np.dot(np.cross(left, right), displacement))
        quartets.append({
            "start_one_based": start + 1,
            "sequence_window": sequence[start:start + 4],
            "generated_ca_pair_distance_squared_hex": _distance_signature(local),
            "boundary_orientation_sign": [
                int(parallel > 0) - int(parallel < 0),
                int(handed > 0) - int(handed < 0),
            ],
        })

    state_rows = []
    for residue in range(len(sequence)):
        window_start = min(max(residue - 1, 0), len(sequence) - 3)
        signature = _material_frame_signature(frames, residue)
        boundary = signature["frame_role"]
        state_rows.append({
            "residue_position_one_based": residue + 1,
            "residue_identity": sequence[residue],
            "sequence_window": sequence[window_start:window_start + 3],
            "sequence_window_start_one_based": window_start + 1,
            "complete_raw_candidate_count": AXIS * AXIS,
            "expected_raw_signature_match_count": 24 if boundary != "interior" else 1,
            "boundary_gauge_axis": (
                "phi" if boundary == "n_boundary"
                else "psi" if boundary == "c_boundary" else None
            ),
            "boundary_gauge_value": 0 if boundary != "interior" else None,
            **signature,
        })

    contacts, step_d2 = _contacts(frames)
    orientations = _orientation_signatures(ca)
    return {
        "schema": "fold-protein-material-relation/v1",
        "status": "derived",
        "result_type": "transferable sequence-only forward-forced material constitution",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "relation": (
            "The frozen transfer command maps constituted residue material and "
            "SFT binary/colour/One addresses to one lattice state; its generated "
            "frames then close the unchanged Material Architecture V1 relation."
        ),
        "derivation_boundary": (
            "The command was observationally derived from the protected ubiquitin "
            "witness before registration. Runtime uses only sequence and command; "
            "experimental targets and comparison scores are inaccessible."
        ),
        "prohibitions": [
            "no weights", "no fitted parameters", "no reward",
            "no candidate ordering", "no runtime experimental target",
            "no runtime protected witness", "no comparison score",
        ],
        "lattice_axis_count": AXIS,
        "lattice_state_count": AXIS * AXIS,
        "colour_window_residues": COLOUR,
        "binary_overlap_residues": BINARY,
        "one_advance_residues": ONE,
        "sequence": sequence,
        "sequence_sha256": sha256(sequence.encode()).hexdigest(),
        "residue_count": len(sequence),
        "sequence_window_count": len(windows),
        "distinct_sequence_window_count": len(windows),
        "window_overlap_count": max(0, len(windows) - 1),
        "window_relation": windows,
        "quartet_relation": quartets,
        "material_state_relation": state_rows,
        "generated_geometry": {
            "spatial_one_squared_hex": float(step_d2).hex(),
            "contact_relation": [
                {
                    "residue_positions_one_based": list(pair),
                    "sequence_pair": sequence[pair[0] - 1] + sequence[pair[1] - 1],
                    "atom_contact_count": count,
                    "long_range": pair[1] - pair[0] >= 4,
                }
                for pair, count in sorted(contacts.items())
            ],
            "long_range_orientation_relation": [
                {
                    "residue_positions_one_based": list(pair),
                    "parallel_sign": signs[0],
                    "handedness_sign": signs[1],
                }
                for pair, signs in sorted(orientations.items())
            ],
        },
        "transfer_command_sha256": sha256(
            (json.dumps(command, sort_keys=True) + "\n").encode()
        ).hexdigest(),
        "command_trace_sha256": sha256(
            json.dumps(material["command_trace"], sort_keys=True).encode()
        ).hexdigest(),
    }
