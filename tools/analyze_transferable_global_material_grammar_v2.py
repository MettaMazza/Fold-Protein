#!/usr/bin/env python3
"""Exhaust the SFT global material-address grammar against the witness.

V1 closes the local depth-two grammar.  V2 adds only globally generated SFT
addresses: prefix/suffix material, binary-colour block scales, complements,
fold iterates, and recurrent prior generated geometry.  It still contains no
target coordinates, structural labels, statistical model, fitted coefficient,
weight, reward, or comparison score.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from tools.analyze_transferable_material_grammar_v1 import (
    AXIS, BINARY, COLOUR, ONE, WITNESS, circular_error, file_sha256,
    generated_grammar, measured_row, mod_vector, primitive_vectors,
    residue_material, retain_best,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "verify/transferable_global_material_grammar_analysis_v2.json"
BLOCK_SCALES = (
    BINARY, COLOUR, BINARY * COLOUR, BINARY ** COLOUR,
    COLOUR * (BINARY ** COLOUR),
)


def prefix(values: tuple[int, ...]) -> tuple[int, ...]:
    total = 0
    result = []
    for value in values:
        total += value
        result.append(total)
    return tuple(result)


def suffix(values: tuple[int, ...]) -> tuple[int, ...]:
    total = 0
    result = [0] * len(values)
    for index in range(len(values) - ONE, -ONE, -ONE):
        total += values[index]
        result[index] = total
    return tuple(result)


def preceding_block(values: tuple[int, ...], size: int) -> tuple[int, ...]:
    result = []
    for index in range(len(values)):
        start = max(0, index - size + ONE)
        result.append(sum(values[start:index + ONE]))
    return tuple(result)


def global_primitives(sequence: str, states: list[int]) -> dict[str, tuple[int, ...]]:
    primitives = primitive_vectors(sequence, states)
    material = residue_material(sequence)
    count = len(sequence)
    position = tuple(range(ONE, count + ONE))
    primitives["reverse_position"] = mod_vector(count + ONE - value for value in position)
    primitives["chain_count"] = (count % AXIS,) * count
    for name, values in material.items():
        before = prefix(values)
        after = suffix(values)
        primitives[f"prefix_{name}"] = mod_vector(before)
        primitives[f"suffix_{name}"] = mod_vector(after)
        primitives[f"material_complement_{name}"] = mod_vector(
            after[index] - before[index] for index in range(count)
        )
        for size in BLOCK_SCALES:
            primitives[f"block_{size}_{name}"] = mod_vector(
                preceding_block(values, size)
            )
            primitives[f"block_address_{size}_{name}"] = mod_vector(
                sum(values[max(0, index - size + ONE):index + ONE])
                + (index // size)
                for index in range(count)
            )

    phi = tuple(state // AXIS for state in states)
    psi = tuple(state % AXIS for state in states)
    prior_phi = primitives["prior_phi"]
    prior_psi = primitives["prior_psi"]
    for name, values in material.items():
        primitives[f"prior_phi_advance_{name}"] = mod_vector(
            prior_phi[index] + values[index] for index in range(count)
        )
        primitives[f"prior_psi_advance_{name}"] = mod_vector(
            prior_psi[index] + values[index] for index in range(count)
        )
        primitives[f"prior_phi_fold_{name}"] = mod_vector(
            BINARY * prior_phi[index] + values[index] for index in range(count)
        )
        primitives[f"prior_psi_fold_{name}"] = mod_vector(
            BINARY * prior_psi[index] + values[index] for index in range(count)
        )
    primitives["prior_state_axis_sum"] = mod_vector(
        left + right for left, right in zip(prior_phi, prior_psi)
    )
    primitives["prior_state_axis_difference"] = mod_vector(
        left - right for left, right in zip(prior_phi, prior_psi)
    )
    primitives["protected_phi_for_measurement_only"] = mod_vector(phi)
    primitives["protected_psi_for_measurement_only"] = mod_vector(psi)
    # Targets are removed before grammar generation; their presence here makes
    # the exclusion mechanically checkable rather than implicit.
    return primitives


def main() -> None:
    witness = json.loads(WITNESS.read_text())
    sequence = witness["sequence"]
    states = [int(state) for state in witness["states"]]
    targets = {
        "phi": tuple(state // AXIS for state in states),
        "psi": tuple(state % AXIS for state in states),
    }
    primitives = global_primitives(sequence, states)
    forbidden = {
        "protected_phi_for_measurement_only",
        "protected_psi_for_measurement_only",
    }
    grammar_primitives = {
        name: values for name, values in primitives.items() if name not in forbidden
    }
    if forbidden & set(grammar_primitives):
        raise RuntimeError("protected target axes entered the generated grammar")

    best = {"phi": [], "psi": []}
    exact = {"phi": [], "psi": []}
    generated = 0
    for expression, vector in generated_grammar(grammar_primitives):
        generated += ONE
        if "protected_" in expression:
            raise RuntimeError("protected target expression entered grammar")
        for axis_name, target in targets.items():
            row = measured_row(expression, vector, target)
            retain_best(best[axis_name], row)
            if row["exact_positions"] == len(target):
                exact[axis_name].append(row)

    result = {
        "schema": "fold-protein-transferable-global-material-grammar-analysis/v2",
        "status": "complete",
        "result_type": "protected-witness forward-forcing diagnostic",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "grammar": {
            "axis_modulus": AXIS,
            "colour_window": COLOUR,
            "binary_overlap": BINARY,
            "one_advance": ONE,
            "block_scales": list(BLOCK_SCALES),
            "primitive_count": len(grammar_primitives),
            "deduplicated_expression_count": generated,
            "target_axis_primitives_explicitly_excluded": sorted(forbidden),
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
            "This exhausts the declared global address grammar. A direct "
            "transfer architecture is admitted only if both axes close "
            "exactly; otherwise a generated spatial relation must be derived "
            "rather than choosing the strongest partial expression."
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
        "primitive_count": len(grammar_primitives),
        "deduplicated_expression_count": generated,
        "best_phi_exact_positions": best["phi"][0]["exact_positions"],
        "best_psi_exact_positions": best["psi"][0]["exact_positions"],
        "complete_exact_paired_relation_count": result[
            "complete_exact_paired_relation_count"
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
