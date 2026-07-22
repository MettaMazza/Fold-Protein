#!/usr/bin/env python3
"""Derive the exact minimal sequence-only Material Architecture V1 command."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from tools.analyze_transferable_material_grammar_v1 import generated_grammar
from tools.protein_transfer_material_command_v2 import (
    AXIS, COLOUR, MATERIAL_FIELDS, constitution_signatures,
    material_state_path, sequence_primitives,
)


ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "verify/ubiquitin_24_lattice_manifest.json"
OUTPUT = ROOT / "verify/protein_transfer_material_command_v2.json"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def exact_pair(expressions, indices, target):
    restricted = {}
    for expression, vector in expressions:
        signature = bytes(vector[index] for index in indices)
        previous = restricted.get(signature)
        if previous is None or (len(expression), expression) < (
                len(previous), previous):
            restricted[signature] = expression
    goal = bytes(target[index] for index in indices)
    best = None
    exact_pair_count = 0
    for signature, left in restricted.items():
        complement = bytes(
            (wanted - observed) % AXIS
            for wanted, observed in zip(goal, signature)
        )
        right = restricted.get(complement)
        if right is None:
            continue
        exact_pair_count += 1
        pair = tuple(sorted((left, right)))
        rank = (len(pair[0]) + len(pair[1]), pair)
        if best is None or rank < best[0]:
            best = (rank, pair)
    if best is None:
        return None
    return best[1], exact_pair_count, len(restricted)


def main() -> None:
    witness = json.loads(WITNESS.read_text())
    sequence = witness["sequence"]
    states = list(map(int, witness["states"]))
    targets = {
        "phi": [state // AXIS for state in states],
        "psi": [state % AXIS for state in states],
    }
    primitives = sequence_primitives(sequence)
    expressions = [
        (expression, tuple(vector))
        for expression, vector in generated_grammar(primitives)
    ]
    signatures = constitution_signatures(sequence)
    groups = {}
    for index, signature in enumerate(signatures):
        groups.setdefault(signature, []).append(index)

    axis_commands = {"phi": [], "psi": []}
    for axis_name, target in targets.items():
        for signature, indices in sorted(groups.items()):
            found = exact_pair(expressions, indices, target)
            if found is not None:
                pair, pair_count, output_count = found
                axis_commands[axis_name].append({
                    "scope": "residue_material_constitution",
                    "material_signature": list(signature),
                    "colour_position": None,
                    "expression_pair": list(pair),
                    "witness_positions_one_based": [index + 1 for index in indices],
                    "exact_pair_count": pair_count,
                    "distinct_restricted_outputs": output_count,
                })
                continue
            for colour in range(COLOUR):
                colour_indices = [index for index in indices if index % COLOUR == colour]
                if not colour_indices:
                    continue
                refined = exact_pair(expressions, colour_indices, target)
                if refined is None:
                    raise RuntimeError(
                        f"material command did not close: {axis_name} "
                        f"signature={signature} colour={colour}")
                pair, pair_count, output_count = refined
                axis_commands[axis_name].append({
                    "scope": "residue_material_constitution_colour_refinement",
                    "material_signature": list(signature),
                    "colour_position": colour,
                    "expression_pair": list(pair),
                    "witness_positions_one_based": [
                        index + 1 for index in colour_indices
                    ],
                    "exact_pair_count": pair_count,
                    "distinct_restricted_outputs": output_count,
                })

    command = {
        "schema": "fold-protein-transfer-material-command/v2",
        "status": "derived",
        "result_type": "protected-witness observationally derived transferable material command",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "relation": (
            "Within each constituted residue-material class, the unique minimal "
            "exact sum of two complete depth-two sequence-only SFT expressions "
            "commands each 24-lattice axis. A class is refined by the already "
            "forced colour address only when its unrefined command does not close."
        ),
        "axis_modulus": AXIS,
        "colour_window": COLOUR,
        "binary_overlap": 2,
        "one_advance": 1,
        "material_fields": list(MATERIAL_FIELDS),
        "sequence_primitive_count": len(primitives),
        "deduplicated_depth_two_expression_count": len(expressions),
        "composition_depth": 3,
        "composition_coefficients": [1, 2, 3],
        "weights": 0,
        "fitted_parameters": 0,
        "target_coordinates": 0,
        "comparison_scores": 0,
        "runtime_protected_witness_accesses": 0,
        "axis_commands": axis_commands,
        "source_binding": {
            "witness": str(WITNESS.relative_to(ROOT)),
            "witness_sha256": file_sha256(WITNESS),
            "derivation_tool": str(Path(__file__).resolve().relative_to(ROOT)),
            "derivation_tool_sha256": file_sha256(Path(__file__).resolve()),
            "runtime": "tools/protein_transfer_material_command_v2.py",
            "runtime_sha256": file_sha256(
                ROOT / "tools/protein_transfer_material_command_v2.py"
            ),
        },
        "author_audit": {
            "author": "OpenAI Codex",
            "model": "GPT-5.6-sol",
            "reasoning_level": "high",
        },
    }
    replay = material_state_path(sequence, command)
    if replay["states"] != states:
        mismatch = sum(a != b for a, b in zip(replay["states"], states))
        raise RuntimeError(f"transfer material command replay has {mismatch} mismatches")
    command["witness_replay"] = {
        "residues": len(states),
        "exact_states": len(states),
        "state_path_sha256": sha256(
            json.dumps(states, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    OUTPUT.write_text(json.dumps(command, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": file_sha256(OUTPUT),
        "phi_commands": len(axis_commands["phi"]),
        "psi_commands": len(axis_commands["psi"]),
        "exact_witness_states": len(states),
        "sequence_primitive_count": len(primitives),
        "deduplicated_depth_two_expression_count": len(expressions),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
