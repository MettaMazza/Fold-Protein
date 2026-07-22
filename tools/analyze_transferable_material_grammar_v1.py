#!/usr/bin/env python3
"""Exhaust the first SFT material-command grammar against the protected witness.

This is a development diagnostic, not a runtime selector.  It asks whether one
target-independent modular relation over already constituted residue material,
the colour window, binary overlap, One advance, and generated prior state can
produce either 24-lattice axis.  The protected path is read only as the declared
development witness used to measure each complete grammar member.

No protein-language model, statistical structure prior, target coordinate,
comparison score, fitted coefficient, reward, or conventional secondary-
structure label enters the grammar.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from tools.backbone_hydrogen_bond_constitution_v2 import NON_DONOR_RESIDUES
from tools.residue_charge_constitution_v1 import CHARGE_SIGN
from tools.residue_partition_v1 import HYDROPHOBIC_PACKING
from tools.sidechain_graph_spatial_exclusion_v1 import (
    SIDECHAIN_GRAPH_SPATIAL_CENSUS,
)


ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "verify/ubiquitin_24_lattice_manifest.json"
OUTPUT = ROOT / "verify/transferable_material_grammar_analysis_v1.json"
AXIS = 24
COLOUR = 3
BINARY = 2
ONE = 1


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def mod_vector(values) -> tuple[int, ...]:
    return tuple(int(value) % AXIS for value in values)


def circular_error(candidate: tuple[int, ...], target: tuple[int, ...]) -> int:
    return sum(min((left - right) % AXIS, (right - left) % AXIS)
               for left, right in zip(candidate, target))


def measured_row(expression: str, candidate: tuple[int, ...],
                 target: tuple[int, ...]) -> dict:
    first = len(target) // BINARY
    return {
        "expression": expression,
        "exact_positions": sum(left == right for left, right in zip(candidate, target)),
        "first_half_exact_positions": sum(
            candidate[index] == target[index] for index in range(first)),
        "second_half_exact_positions": sum(
            candidate[index] == target[index] for index in range(first, len(target))),
        "total_circular_axis_error": circular_error(candidate, target),
        "output_sha256": sha256(
            json.dumps(candidate, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def retain_best(rows: list[dict], row: dict, capacity: int = AXIS) -> None:
    rows.append(row)
    rows.sort(key=lambda item: (
        -item["exact_positions"], item["total_circular_axis_error"],
        item["expression"],
    ))
    del rows[capacity:]


def residue_material(sequence: str) -> dict[str, tuple[int, ...]]:
    graphs = SIDECHAIN_GRAPH_SPATIAL_CENSUS["graphs"]
    values: dict[str, list[int]] = {
        "atom": [], "bond": [], "branch": [], "cycle": [],
        "charge": [], "packing": [], "donor": [], "position": [],
        "binary_position": [], "colour_position": [],
    }
    for position, residue in enumerate(sequence, start=ONE):
        graph = graphs[residue]
        values["atom"].append(len(graph["atoms"]))
        values["bond"].append(len(graph["bonds"]))
        values["branch"].append(graph["branch_atom_count"])
        values["cycle"].append(graph["cycle_rank"])
        values["charge"].append(CHARGE_SIGN[residue])
        values["packing"].append(int(residue in HYDROPHOBIC_PACKING))
        values["donor"].append(int(residue not in NON_DONOR_RESIDUES))
        values["position"].append(position)
        values["binary_position"].append((position - ONE) % BINARY)
        values["colour_position"].append((position - ONE) % COLOUR)
    return {name: tuple(rows) for name, rows in values.items()}


def shifted(values: tuple[int, ...], offset: int) -> tuple[int, ...]:
    result = []
    for index in range(len(values)):
        source = index + offset
        result.append(values[source] if 0 <= source < len(values) else 0)
    return tuple(result)


def primitive_vectors(sequence: str, states: list[int]) -> dict[str, tuple[int, ...]]:
    material = residue_material(sequence)
    primitives: dict[str, tuple[int, ...]] = {}
    for name, values in material.items():
        for offset, label in ((-ONE, "left"), (0, "self"), (ONE, "right")):
            primitives[f"{label}_{name}"] = mod_vector(shifted(values, offset))
        left = shifted(values, -ONE)
        right = shifted(values, ONE)
        primitives[f"window_{name}"] = mod_vector(
            left[index] + values[index] + right[index]
            for index in range(len(values))
        )
        primitives[f"advance_{name}"] = mod_vector(
            right[index] - left[index] for index in range(len(values))
        )

    phi = tuple(state // AXIS for state in states)
    psi = tuple(state % AXIS for state in states)
    primitives["prior_phi"] = mod_vector(shifted(phi, -ONE))
    primitives["prior_psi"] = mod_vector(shifted(psi, -ONE))
    primitives["binary_prior_phi"] = mod_vector(shifted(phi, -BINARY))
    primitives["binary_prior_psi"] = mod_vector(shifted(psi, -BINARY))
    primitives["one"] = (ONE,) * len(sequence)
    primitives["binary"] = (BINARY,) * len(sequence)
    primitives["colour"] = (COLOUR,) * len(sequence)
    return primitives


def generated_grammar(primitives: dict[str, tuple[int, ...]]):
    """Yield the complete declared depth-two grammar, deduplicated by output."""
    seen: dict[tuple[int, ...], str] = {}

    def admit(expression: str, values) -> None:
        vector = mod_vector(values)
        previous = seen.get(vector)
        if previous is None or (len(expression), expression) < (len(previous), previous):
            seen[vector] = expression

    for name, vector in sorted(primitives.items()):
        admit(name, vector)
        admit(f"fold({name})", (BINARY * value for value in vector))
        admit(f"antipode({name})", (-value for value in vector))
        admit(f"{name}+One", (value + ONE for value in vector))
        admit(f"{name}+colour", (value + COLOUR for value in vector))

    leaves = sorted(primitives.items())
    for left_index, (left_name, left) in enumerate(leaves):
        for right_name, right in leaves[left_index:]:
            admit(f"({left_name}+{right_name})",
                  (a + b for a, b in zip(left, right)))
            admit(f"({left_name}-{right_name})",
                  (a - b for a, b in zip(left, right)))
            admit(f"({right_name}-{left_name})",
                  (b - a for a, b in zip(left, right)))
            admit(f"({left_name}*{right_name})",
                  (a * b for a, b in zip(left, right)))
            admit(f"fold({left_name})+{right_name}",
                  (BINARY * a + b for a, b in zip(left, right)))
            admit(f"{left_name}+fold({right_name})",
                  (a + BINARY * b for a, b in zip(left, right)))
            admit(f"colour*{left_name}+{right_name}",
                  (COLOUR * a + b for a, b in zip(left, right)))
            admit(f"{left_name}+colour*{right_name}",
                  (a + COLOUR * b for a, b in zip(left, right)))

    for vector, expression in seen.items():
        yield expression, vector


def main() -> None:
    witness = json.loads(WITNESS.read_text())
    sequence = witness["sequence"]
    states = [int(state) for state in witness["states"]]
    if len(sequence) != len(states):
        raise RuntimeError("material grammar witness length drifted")
    phi_target = tuple(state // AXIS for state in states)
    psi_target = tuple(state % AXIS for state in states)
    primitives = primitive_vectors(sequence, states)

    best = {"phi": [], "psi": []}
    exact = {"phi": [], "psi": []}
    generated = 0
    for expression, vector in generated_grammar(primitives):
        generated += ONE
        for axis_name, target in (("phi", phi_target), ("psi", psi_target)):
            row = measured_row(expression, vector, target)
            retain_best(best[axis_name], row)
            if row["exact_positions"] == len(target):
                exact[axis_name].append(row)

    result = {
        "schema": "fold-protein-transferable-material-grammar-analysis/v1",
        "status": "complete",
        "result_type": "protected-witness forward-forcing diagnostic",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "grammar": {
            "axis_modulus": AXIS,
            "colour_window": COLOUR,
            "binary_overlap": BINARY,
            "one_advance": ONE,
            "primitive_count": len(primitives),
            "deduplicated_expression_count": generated,
            "operations": [
                "identity", "fold", "antipode", "One translation",
                "colour translation", "addition", "subtraction",
                "multiplication", "binary fold composition",
                "colour composition",
            ],
            "coefficients": [ONE, BINARY, COLOUR],
            "fitted_coefficients": 0,
            "weights": 0,
            "target_coordinates": 0,
            "comparison_scores": 0,
            "statistical_or_learned_model_queries": 0,
        },
        "witness": {
            "path": str(WITNESS.relative_to(ROOT)),
            "sha256": file_sha256(WITNESS),
            "sequence_sha256": sha256(sequence.encode()).hexdigest(),
            "residues": len(sequence),
        },
        "best_phi_relations": best["phi"],
        "best_psi_relations": best["psi"],
        "complete_exact_phi_relations": exact["phi"],
        "complete_exact_psi_relations": exact["psi"],
        "complete_exact_paired_relation_count": (
            len(exact["phi"]) * len(exact["psi"])
        ),
        "interpretation_boundary": (
            "This exhausts the declared first depth-two transferable material "
            "grammar. It admits a direct architecture only if both axes have "
            "complete exact relations; otherwise the next derivation must add "
            "a newly engine-closed generated-geometry relation rather than "
            "choosing a near match."
        ),
        "author_audit": {
            "author": "OpenAI Codex",
            "model": "GPT-5",
            "reasoning_level": "high",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": file_sha256(OUTPUT),
        "primitive_count": len(primitives),
        "deduplicated_expression_count": generated,
        "best_phi_exact_positions": best["phi"][0]["exact_positions"],
        "best_psi_exact_positions": best["psi"][0]["exact_positions"],
        "complete_exact_paired_relation_count": result[
            "complete_exact_paired_relation_count"
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
