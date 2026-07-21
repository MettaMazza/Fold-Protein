#!/usr/bin/env python3
"""V39: select the unique peptide-causal fixed point sealed by V38.

The registered backbone constitution advances residues N to C.  Phi places the
current residue's C atom before psi places the next residue's N atom.  V39
therefore extracts the sole V38 fixed point with direction n_to_c and axis order
phi then psi.  It introduces no search, score, fitted choice or comparison input.
"""
from __future__ import annotations

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    angles_for_state,
    build_backbone_coordinates,
    validate_sequence,
)


CAUSAL_DIRECTION = "n_to_c"
CAUSAL_AXIS_ORDER = (0, 1)
EXPECTED_V38_FIXED_POINTS = 4


def select_state_path_v39(sequence: str, v38_record: dict) -> dict:
    sequence = validate_sequence(sequence)
    if v38_record.get("schema") != "fold-protein-selected-states/v38":
        raise RuntimeError("V39 requires a sealed V38 selected-state record")
    if v38_record.get("sequence") != sequence:
        raise RuntimeError("V39 sequence differs from its registered V38 parent")
    traces = v38_record.get("descent_trace", [])
    coverage = {
        (row["direction"], tuple(row["axis_order"])) for row in traces
    }
    expected = {
        (direction, order)
        for direction in ("n_to_c", "c_to_n")
        for order in ((0, 1), (1, 0))
    }
    if len(traces) != EXPECTED_V38_FIXED_POINTS or coverage != expected:
        raise RuntimeError("V39 parent does not contain the complete V38 order grammar")
    qualifying = [
        row for row in traces
        if row["direction"] == CAUSAL_DIRECTION
        and tuple(row["axis_order"]) == CAUSAL_AXIS_ORDER
        and row["sweeps"][-1]["changed_coordinates"] == 0
    ]
    if len(qualifying) != 1:
        raise RuntimeError(f"V39 requires one peptide-causal fixed point, found {len(qualifying)}")
    selected = qualifying[0]
    states = list(selected["path"]) + [CANONICAL_STATE]
    if len(states) != len(sequence) or any(not 0 <= state < 576 for state in states):
        raise RuntimeError("V39 causal path is outside the complete paired lattice")
    phi = [angles_for_state(state)[0] for state in states]
    psi = [angles_for_state(state)[1] for state in states]
    atoms = build_backbone_coordinates(sequence, phi, psi)
    return {
        "states": states,
        "atoms": atoms,
        "parent_selected_states": v38_record["states"],
        "parent_fixed_point_count": len(traces),
        "causal_direction": CAUSAL_DIRECTION,
        "causal_axis_order": list(CAUSAL_AXIS_ORDER),
        "causal_event_ranks": {"phi": 3, "psi": 4},
        "selected_parent_sweeps": len(selected["sweeps"]),
        "selected_parent_evaluations": selected["evaluations"],
        "final_key": selected["rank_key"],
    }
