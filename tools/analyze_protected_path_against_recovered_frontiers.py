#!/usr/bin/env python3
"""Compare the protected 0.9891 lattice path with every blind frontier state.

This is a development-only, target-assisted comparison.  The protected state
path is a witness used to discover a target-incapable relation; it is not an
input to any blind runtime.  The comparison preserves every candidate and
reports exact integer censuses wherever possible.  It performs no selection,
fitting, weighting, cutoff search, or target-coordinate access.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from multiprocessing import get_context
from pathlib import Path
from typing import Iterable

import numpy as np

from tools.blind_24_lattice_selector_v3 import (
    CANONICAL_STATE,
    angles_for_state,
    build_backbone_coordinates,
)
from tools.blind_24_lattice_selector_v42 import (
    CONTACT_INNER_SQUARED_DENOMINATOR,
)


ROOT = Path(__file__).resolve().parents[1]
PROTECTED_MANIFEST = ROOT / "verify/ubiquitin_24_lattice_manifest.json"
RECOVERY_SUMMARY = (
    ROOT / "verify/historical_positive_frontier_recovery_summary_v1.json"
)
OUTPUT = ROOT / "verify/protected_path_recovered_frontier_comparison_v1.json"
ACTIVE_FRONTIERS = (
    ROOT / "verify/development_runs/ubiquitin_v43_one_cycle_frontier_l76_20260721/frontier.json",
    ROOT / "verify/development_runs/ubiquitin_v44_connected_cycle_fixed_point_l76_20260721/frontier.json",
    ROOT / "verify/development_runs/ubiquitin_v45_boundary_axis_fixed_point_l76_20260721/frontier.json",
)
WORKERS = 24


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_json_sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def _states_from_rows(rows: Iterable[dict], *, append_canonical: bool = False):
    result = []
    for row in rows:
        # When a path is explicitly requested, prefer it: V42's three
        # connected trace objects are also referenced by its emitted frontier
        # and consequently carry both the 75 active states and a 76-state
        # convenience field.
        states = row.get("path") if append_canonical else row.get("states", row.get("path"))
        if states is None:
            raise RuntimeError("frontier row has neither states nor path")
        states = list(map(int, states))
        if append_canonical:
            states.append(CANONICAL_STATE)
        result.append(states)
    return result


def _load_recovery_states(recovery: dict) -> tuple[list[list[int]], Path]:
    evaluation = ROOT / recovery["evaluation_path"]
    frontier = evaluation.parent / "frontier.json"
    if frontier.exists():
        record = json.loads(frontier.read_text())
        if recovery["candidate_count"] == 8192:
            rows = record["component_cube_trace"]
            states = _states_from_rows(rows, append_canonical=True)
        else:
            rows = record.get("candidates", record.get("frontier"))
            if rows is None:
                raise RuntimeError(f"unrecognised frontier schema: {frontier}")
            states = _states_from_rows(rows)
        return states, frontier

    selected_candidates = (
        evaluation.parent / "selected_states.json",
        evaluation.parent.parent / "selected_states.json",
    )
    selected = next((path for path in selected_candidates if path.exists()), None)
    if selected is None:
        raise RuntimeError(f"no preserved candidate source found for {evaluation}")
    record = json.loads(selected.read_text())
    if "reconciliation_trace" in record:
        rows = record["reconciliation_trace"]
    elif "descent_trace" in record:
        rows = record["descent_trace"]
    elif "fixed_point_trace" in record:
        rows = record["fixed_point_trace"]
    else:
        raise RuntimeError(f"unrecognised preserved frontier: {selected}")
    return _states_from_rows(rows, append_canonical=True), selected


def load_all_candidates() -> tuple[list[dict], list[dict], list[dict]]:
    summary = json.loads(RECOVERY_SUMMARY.read_text())
    recovered = []
    sources = []
    for recovery_index, recovery in enumerate(summary["recoveries"]):
        states_rows, source = _load_recovery_states(recovery)
        if len(states_rows) != recovery["candidate_count"]:
            raise RuntimeError(
                f"candidate census mismatch for {recovery['run_id']}: "
                f"{len(states_rows)} != {recovery['candidate_count']}"
            )
        sources.append({
            "kind": "recovered",
            "run_id": recovery["run_id"],
            "candidate_count": len(states_rows),
            "candidate_source": str(source.relative_to(ROOT)),
            "candidate_source_sha256": file_sha256(source),
            "evaluation_path": recovery["evaluation_path"],
            "evaluation_sha256": recovery["evaluation_sha256"],
        })
        for candidate_index, states in enumerate(states_rows):
            recovered.append({
                "scope": "recovered",
                "recovery_index": recovery_index,
                "run_id": recovery["run_id"],
                "candidate_index": candidate_index,
                "states": states,
            })
    if len(recovered) != summary["candidate_count"]:
        raise RuntimeError(
            f"complete recovery census drifted: {len(recovered)} != "
            f"{summary['candidate_count']}"
        )

    active = []
    for path in ACTIVE_FRONTIERS:
        record = json.loads(path.read_text())
        rows = record["frontier"]
        sources.append({
            "kind": "active_extension",
            "run_id": record["run_id"],
            "candidate_count": len(rows),
            "candidate_source": str(path.relative_to(ROOT)),
            "candidate_source_sha256": file_sha256(path),
        })
        for candidate_index, states in enumerate(_states_from_rows(rows)):
            active.append({
                "scope": "active_extension",
                "run_id": record["run_id"],
                "candidate_index": candidate_index,
                "states": states,
            })
    return recovered, active, sources


def generated_frames(sequence: str, states: list[int]) -> tuple[np.ndarray, np.ndarray]:
    length = len(states)
    atoms = build_backbone_coordinates(
        sequence[:length],
        [angles_for_state(state)[0] for state in states],
        [angles_for_state(state)[1] for state in states],
    )
    residues = [dict() for _ in states]
    for atom in atoms:
        residues[atom["resnum"] - 1][atom["name"]] = np.asarray(
            atom["coord"], dtype=float
        )
    if any(set(row) != {"N", "CA", "C"} for row in residues):
        raise RuntimeError("generated backbone frame is incomplete")
    frames = np.asarray([[row["N"], row["CA"], row["C"]] for row in residues])
    return frames, frames[:, 1, :]


def pair_distance_vector(coordinates: np.ndarray) -> np.ndarray:
    count = len(coordinates)
    return np.asarray([
        np.linalg.norm(coordinates[right] - coordinates[left])
        for left in range(count)
        for right in range(left + 1, count)
    ])


def drmsd(left: np.ndarray, right: np.ndarray) -> float:
    if len(left) < 2:
        return 0.0
    delta = pair_distance_vector(left) - pair_distance_vector(right)
    return float(np.sqrt(np.mean(delta * delta)))


def window_drmsds(candidate: np.ndarray, witness: np.ndarray, width: int):
    values = [
        drmsd(candidate[start:start + width], witness[start:start + width])
        for start in range(len(candidate) - width + 1)
    ]
    if not values:
        return {"count": 0, "sum": 0.0, "minimum": None, "maximum": None}
    return {
        "count": len(values),
        "sum": float(sum(values)),
        "minimum": float(min(values)),
        "maximum": float(max(values)),
    }


def contact_set(frames: np.ndarray) -> tuple[set[tuple[int, int]], int, float]:
    ca = frames[:, 1, :]
    step_d2 = float(np.mean(np.sum(np.diff(ca, axis=0) ** 2, axis=1)))
    if not np.isfinite(step_d2) or step_d2 <= 0:
        raise RuntimeError("generated adjacent C-alpha One is degenerate")
    contacts = set()
    atom_contacts = 0
    for left in range(len(frames)):
        for right in range(left + 2, len(frames)):
            count = 0
            for left_point in frames[left]:
                for right_point in frames[right]:
                    distance_d2 = float(np.sum((right_point - left_point) ** 2))
                    if step_d2 / CONTACT_INNER_SQUARED_DENOMINATOR <= distance_d2 < step_d2:
                        count += 1
            if count:
                contacts.add((left, right))
                atom_contacts += count
    return contacts, atom_contacts, step_d2


def tangents(ca: np.ndarray) -> np.ndarray:
    result = np.empty_like(ca)
    if len(ca) == 1:
        result[0] = 0.0
        return result
    result[0] = ca[1] - ca[0]
    result[-1] = ca[-1] - ca[-2]
    if len(ca) > 2:
        result[1:-1] = ca[2:] - ca[:-2]
    return result


def sign(value: float) -> int:
    return int(value > 0.0) - int(value < 0.0)


def orientation_signatures(ca: np.ndarray):
    tangent = tangents(ca)
    signatures = {}
    for left in range(len(ca)):
        for right in range(left + 4, len(ca)):
            displacement = ca[right] - ca[left]
            parallel = sign(float(np.dot(tangent[left], tangent[right])))
            handed = sign(float(np.dot(
                np.cross(tangent[left], tangent[right]), displacement
            )))
            signatures[(left, right)] = (parallel, handed)
    return signatures


_SEQUENCE = ""
_WITNESS_STATES: list[int] = []
_WITNESS = {}


def initialise_worker(sequence: str, witness_states: list[int], lengths: list[int]):
    global _SEQUENCE, _WITNESS_STATES, _WITNESS
    _SEQUENCE = sequence
    _WITNESS_STATES = witness_states
    _WITNESS = {}
    for length in lengths:
        frames, ca = generated_frames(sequence, witness_states[:length])
        contacts, atom_contacts, step_d2 = contact_set(frames)
        _WITNESS[length] = {
            "frames": frames,
            "ca": ca,
            "contacts": contacts,
            "atom_contacts": atom_contacts,
            "step_d2": step_d2,
            "orientations": orientation_signatures(ca),
        }


def compare_candidate(candidate: dict) -> dict:
    states = candidate["states"]
    length = len(states)
    witness_states = _WITNESS_STATES[:length]
    witness = _WITNESS[length]
    frames, ca = generated_frames(_SEQUENCE, states)

    exact = sum(a == b for a, b in zip(states, witness_states))
    candidate_axes = [divmod(state, 24) for state in states]
    witness_axes = [divmod(state, 24) for state in witness_states]
    phi_exact = sum(a[0] == b[0] for a, b in zip(candidate_axes, witness_axes))
    psi_exact = sum(a[1] == b[1] for a, b in zip(candidate_axes, witness_axes))
    axis_distances = []
    for left, right in zip(candidate_axes, witness_axes):
        for a, b in zip(left, right):
            direct = abs(a - b)
            axis_distances.append(min(direct, 24 - direct))

    contacts, atom_contacts, step_d2 = contact_set(frames)
    witness_contacts = witness["contacts"]
    common_contacts = contacts & witness_contacts
    union_contacts = contacts | witness_contacts
    long_contacts = {pair for pair in contacts if pair[1] - pair[0] >= 4}
    witness_long_contacts = {
        pair for pair in witness_contacts if pair[1] - pair[0] >= 4
    }
    common_long_contacts = long_contacts & witness_long_contacts
    union_long_contacts = long_contacts | witness_long_contacts

    orientation = orientation_signatures(ca)
    witness_orientation = witness["orientations"]
    parallel_agreements = handed_agreements = joint_agreements = 0
    candidate_zeros = witness_zeros = 0
    for pair, candidate_signature in orientation.items():
        witness_signature = witness_orientation[pair]
        parallel_agreements += candidate_signature[0] == witness_signature[0]
        handed_agreements += candidate_signature[1] == witness_signature[1]
        joint_agreements += candidate_signature == witness_signature
        candidate_zeros += 0 in candidate_signature
        witness_zeros += 0 in witness_signature

    exact_windows = {}
    geometry_windows = {}
    for width in (3, 4):
        count = max(0, length - width + 1)
        exact_windows[str(width)] = {
            "matched": sum(
                states[start:start + width] == witness_states[start:start + width]
                for start in range(count)
            ),
            "count": count,
        }
        geometry_windows[str(width)] = window_drmsds(ca, witness["ca"], width)

    return {
        **{key: value for key, value in candidate.items() if key != "states"},
        "length": length,
        "states_sha256": canonical_json_sha256(states),
        "state": {
            "exact": exact,
            "phi_exact": phi_exact,
            "psi_exact": psi_exact,
            "axis_distance_sum": sum(axis_distances),
            "axis_distance_maximum": max(axis_distances, default=0),
        },
        "overlapping_windows": {
            "exact_state_windows": exact_windows,
            "generated_ca_drmsd": geometry_windows,
        },
        "generated_geometry": {
            "whole_chain_ca_drmsd": drmsd(ca, witness["ca"]),
            "spatial_one_squared": step_d2,
        },
        "contact": {
            "candidate_residue_pairs": len(contacts),
            "witness_residue_pairs": len(witness_contacts),
            "common_residue_pairs": len(common_contacts),
            "union_residue_pairs": len(union_contacts),
            "candidate_atom_pairs": atom_contacts,
            "witness_atom_pairs": witness["atom_contacts"],
            "candidate_long_range_pairs": len(long_contacts),
            "witness_long_range_pairs": len(witness_long_contacts),
            "common_long_range_pairs": len(common_long_contacts),
            "union_long_range_pairs": len(union_long_contacts),
        },
        "long_range_orientation": {
            "pair_count": len(orientation),
            "parallel_sign_agreements": parallel_agreements,
            "handedness_sign_agreements": handed_agreements,
            "joint_sign_agreements": joint_agreements,
            "candidate_zero_signature_pairs": candidate_zeros,
            "witness_zero_signature_pairs": witness_zeros,
        },
    }


def exact_domain_coverage(candidates: list[dict], witness_states: list[int]):
    full = [row for row in candidates if len(row["states"]) == len(witness_states)]
    state_domains = [set() for _ in witness_states]
    phi_domains = [set() for _ in witness_states]
    psi_domains = [set() for _ in witness_states]
    for row in full:
        for index, state in enumerate(row["states"]):
            phi, psi = divmod(state, 24)
            state_domains[index].add(state)
            phi_domains[index].add(phi)
            psi_domains[index].add(psi)
    exact_positions = [
        index + 1 for index, state in enumerate(witness_states)
        if state in state_domains[index]
    ]
    phi_positions = [
        index + 1 for index, state in enumerate(witness_states)
        if divmod(state, 24)[0] in phi_domains[index]
    ]
    psi_positions = [
        index + 1 for index, state in enumerate(witness_states)
        if divmod(state, 24)[1] in psi_domains[index]
    ]
    return {
        "full_length_candidate_count": len(full),
        "protected_exact_state_covered_positions": exact_positions,
        "protected_exact_state_covered_count": len(exact_positions),
        "protected_phi_coordinate_covered_positions": phi_positions,
        "protected_phi_coordinate_covered_count": len(phi_positions),
        "protected_psi_coordinate_covered_positions": psi_positions,
        "protected_psi_coordinate_covered_count": len(psi_positions),
        "position_domain_sizes": [len(domain) for domain in state_domains],
    }


def extrema(rows: list[dict]):
    definitions = {
        "maximum_exact_states": (lambda row: row["state"]["exact"], max),
        "minimum_axis_distance_sum": (
            lambda row: row["state"]["axis_distance_sum"], min
        ),
        "minimum_generated_ca_drmsd": (
            lambda row: row["generated_geometry"]["whole_chain_ca_drmsd"], min
        ),
        "maximum_common_contacts": (
            lambda row: row["contact"]["common_residue_pairs"], max
        ),
        "maximum_common_long_range_contacts": (
            lambda row: row["contact"]["common_long_range_pairs"], max
        ),
        "maximum_joint_orientation_agreements": (
            lambda row: row["long_range_orientation"]["joint_sign_agreements"], max
        ),
    }
    result = {}
    for label, (key, operation) in definitions.items():
        value = operation(key(row) for row in rows)
        winners = [row for row in rows if key(row) == value]
        result[label] = {
            "value": value,
            "tie_count": len(winners),
            "winners": [{
                "scope": row["scope"],
                "run_id": row["run_id"],
                "candidate_index": row["candidate_index"],
                "length": row["length"],
                "states_sha256": row["states_sha256"],
            } for row in winners[:24]],
            "winner_list_truncated": len(winners) > 24,
        }
    return result


def main():
    manifest = json.loads(PROTECTED_MANIFEST.read_text())
    sequence = manifest["sequence"]
    witness_states = list(map(int, manifest["states"]))
    recovered, active, sources = load_all_candidates()
    candidates = recovered + active
    lengths = sorted({len(row["states"]) for row in candidates})
    if any(length > len(witness_states) for length in lengths):
        raise RuntimeError("candidate exceeds protected witness length")

    initialise_worker(sequence, witness_states, lengths)
    with ProcessPoolExecutor(
        max_workers=WORKERS,
        mp_context=get_context("fork"),
        initializer=initialise_worker,
        initargs=(sequence, witness_states, lengths),
    ) as executor:
        comparisons = list(executor.map(compare_candidate, candidates, chunksize=8))

    recovered_rows = [row for row in comparisons if row["scope"] == "recovered"]
    active_rows = [row for row in comparisons if row["scope"] == "active_extension"]
    if len(recovered_rows) != 10336:
        raise RuntimeError("comparison did not preserve all 10,336 recovered rows")

    witness_census = {}
    for length in lengths:
        witness = _WITNESS[length]
        witness_census[str(length)] = {
            "contact_residue_pairs": len(witness["contacts"]),
            "contact_atom_pairs": witness["atom_contacts"],
            "long_range_contact_pairs": sum(
                right - left >= 4 for left, right in witness["contacts"]
            ),
            "long_range_orientation_pairs": len(witness["orientations"]),
            "spatial_one_squared": witness["step_d2"],
        }

    output = {
        "schema": "fold-protein-protected-path-frontier-comparison/v1",
        "status": "complete",
        "result_type": "target-assisted development comparison",
        "official_run": False,
        "authority": "Maria Smith determines scientific conclusions and official runs",
        "purpose": (
            "Use the protected 0.9891 lattice state path only as a development "
            "witness to expose a sequence/generated-geometry relation for a later "
            "target-incapable blind runtime."
        ),
        "prohibitions": [
            "no selection among candidates",
            "no weights",
            "no fitted parameters",
            "no runtime target access",
            "no experimental target coordinates read by this comparison",
        ],
        "author_audit": {
            "author": "OpenAI Codex",
            "model": "GPT-5",
            "reasoning_level": "high",
        },
        "protected_witness": {
            "manifest": str(PROTECTED_MANIFEST.relative_to(ROOT)),
            "manifest_sha256": file_sha256(PROTECTED_MANIFEST),
            "states_sha256": canonical_json_sha256(witness_states),
            "length": len(witness_states),
            "reported_tm_score": manifest["metrics"]["tm_score"],
            "reported_ca_drmsd_angstrom": manifest["metrics"]["ca_drmsd_angstrom"],
            "generated_geometry_census": witness_census,
        },
        "source_binding": {
            "comparison_tool": str(Path(__file__).resolve().relative_to(ROOT)),
            "comparison_tool_sha256": file_sha256(Path(__file__).resolve()),
            "recovery_summary": str(RECOVERY_SUMMARY.relative_to(ROOT)),
            "recovery_summary_sha256": file_sha256(RECOVERY_SUMMARY),
            "candidate_sources": sources,
        },
        "census": {
            "recovered_candidates": len(recovered_rows),
            "active_extension_candidates": len(active_rows),
            "total_compared_candidates": len(comparisons),
            "lengths": {
                str(length): sum(row["length"] == length for row in comparisons)
                for length in lengths
            },
        },
        "recovered_full_length_domain_coverage": exact_domain_coverage(
            recovered, witness_states
        ),
        "all_full_length_domain_coverage": exact_domain_coverage(
            candidates, witness_states
        ),
        "recovered_extrema": extrema(recovered_rows),
        "all_extrema": extrema(comparisons),
        "comparisons": comparisons,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": file_sha256(OUTPUT),
        "census": output["census"],
        "recovered_full_length_domain_coverage": output[
            "recovered_full_length_domain_coverage"
        ],
        "recovered_extrema": output["recovered_extrema"],
        "all_extrema": output["all_extrema"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
