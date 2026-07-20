#!/usr/bin/env python3
"""V34: V3 ordering composed with the engine-closed V2 alpha/beta domain.

The selection order, lattice census, target-incapable geometry, residue
partition, beam capacity, and deterministic tie break are reused byte-for-byte
from the admitted V3 constitution.  V34 changes one complete architectural
layer: every C-alpha-active residue now enumerates exactly the two canonical
backbone forms uniquely closed by the V2 Protein engine.
"""
from __future__ import annotations

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    LATTICE_DEGREES,
    _candidate_key,
    angles_for_state,
    build_backbone_coordinates,
    forced_beam_width,
    validate_sequence,
)


BINARY_COUNT = 2
COLOUR_COUNT = 3


def _whole_power(base: int, exponent: int) -> int:
    value = 1
    for _ in range(exponent):
        value *= base
    return value


def closed_angle_domain() -> dict[str, int]:
    """Generate the two V2 forms from the counted lattice routes."""
    axis = _whole_power(BINARY_COUNT, COLOUR_COUNT) * COLOUR_COUNT
    if axis != len(LATTICE_DEGREES):
        raise RuntimeError("V34 angle axis differs from the V2 counted lattice")
    step = 360 // axis
    alpha_phi = -(axis // (BINARY_COUNT * COLOUR_COUNT)) * step
    alpha_psi = -(axis // _whole_power(BINARY_COUNT, COLOUR_COUNT)) * step
    beta_phi = -(axis // COLOUR_COUNT) * step
    beta_psi = (COLOUR_COUNT * COLOUR_COUNT) * step

    def state(phi: int, psi: int) -> int:
        if phi not in LATTICE_DEGREES or psi not in LATTICE_DEGREES:
            raise RuntimeError("V2 canonical form lies outside the counted lattice")
        return LATTICE_DEGREES.index(phi) * axis + LATTICE_DEGREES.index(psi)

    domain = {"alpha": state(alpha_phi, alpha_psi),
              "beta": state(beta_phi, beta_psi)}
    if len(set(domain.values())) != BINARY_COUNT:
        raise RuntimeError("V34 closed alpha/beta domain is not binary and unique")
    expected_angles = {
        "alpha": (alpha_phi, alpha_psi),
        "beta": (beta_phi, beta_psi),
    }
    for mode, selected_state in domain.items():
        phi, psi = angles_for_state(selected_state)
        observed = (round(phi * 180 / 3.141592653589793),
                    round(psi * 180 / 3.141592653589793))
        if observed != expected_angles[mode]:
            raise RuntimeError(f"V34 {mode} state does not replay its V2 form")
    return domain


def select_state_path_v34(sequence: str) -> dict:
    sequence = validate_sequence(sequence)
    domain = closed_angle_domain()
    candidate_states = tuple(sorted(domain.values()))
    state_modes = {state: mode for mode, state in domain.items()}
    beam_width = forced_beam_width()
    if len(sequence) == 1:
        phi, psi = angles_for_state(CANONICAL_STATE)
        atoms = build_backbone_coordinates(sequence, [phi], [psi])
        return {
            "states": [CANONICAL_STATE], "modes": ["inactive"],
            "score_trace": [], "final_key": [0, 1.0, 0.0],
            "atoms": atoms, "closed_domain": domain,
        }

    beam = [((0, 1.0, 0.0), tuple())]
    score_trace = []
    for index in range(len(sequence) - 1):
        expanded = []
        for _, path in beam:
            for state in candidate_states:
                candidate = list(path) + [state]
                expanded.append((_candidate_key(sequence, candidate), tuple(candidate)))
        expected_expanded = len(beam) * BINARY_COUNT
        if len(expanded) != expected_expanded:
            raise RuntimeError("V34 did not enumerate the complete binary residue domain")
        expanded.sort(key=lambda item: (item[0], item[1]))
        beam = expanded[:beam_width]
        score_trace.append({
            "active_state": index,
            "candidate_domain": list(candidate_states),
            "expanded": len(expanded),
            "retained": len(beam),
            "best_key": list(beam[0][0]),
            "worst_key": list(beam[-1][0]),
        })

    final_key, active_path = beam[0]
    states = list(active_path) + [CANONICAL_STATE]
    modes = [state_modes[state] for state in active_path] + ["inactive"]
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "modes": modes,
        "score_trace": score_trace,
        "final_key": list(final_key),
        "atoms": atoms,
        "closed_domain": domain,
    }
