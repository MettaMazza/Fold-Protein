#!/usr/bin/env python3
"""Verify and evaluate sealed degree-two tertiary path selector V30."""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from calculate_tm import compute_tm, parse_ca  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(manifest_path, sealed_dir):
    manifest_path, sealed_dir = Path(manifest_path).resolve(), Path(sealed_dir).resolve()
    manifest = json.loads(manifest_path.read_text())
    seal = json.loads((sealed_dir / "seal.json").read_text())
    if (manifest.get("schema") != "fold-protein-blind-selector/v30"
            or seal.get("schema") != "fold-protein-blind-seal/v30"):
        raise RuntimeError("invalid V30 seal; target access forbidden")
    for field, path in {
            "protocol_manifest_sha256": manifest_path,
            "selector_input_sha256": sealed_dir / "selector_input.json",
            "selected_states_sha256": sealed_dir / "selected_states.json",
            "prediction_pdb_sha256": sealed_dir / "prediction.pdb"}.items():
        if seal.get(field) != sha(path):
            raise RuntimeError(f"V30 seal mismatch: {field}")
    states = json.loads((sealed_dir / "selected_states.json").read_text())
    lineage_manifest = json.loads((ROOT / "verify/blind_selector_v29.json").read_text())
    binding = lineage_manifest["parent_records"][seal["v28_run_id"]]
    for name in ("v25", "v26_1", "v27", "v28", "domain"):
        if sha(ROOT / binding[name + "_path"]) != binding[name + "_sha256"]:
            raise RuntimeError("V30 branch lineage drift")
    census = states["tertiary_census"]
    if (len(states["states"]) != len(states["sequence"])
            or census["path_edge_count"] != census["segment_count"] - 1
            or max(census["body_degrees"], default=0) > 2
            or any(row["retained_paths"] != 24 for row in states["assembly_trace"])):
        raise RuntimeError("V30 tertiary path closure mismatch")
    for relative, expected in manifest["source_sha256"].items():
        if sha(ROOT / relative) != expected:
            raise RuntimeError(f"V30 source drift: {relative}")
    return seal, states


def evaluate(manifest_path, sealed_dir, target_path, output_path):
    seal, states = verify(manifest_path, sealed_dir)
    sealed_dir, target_path, output_path = (
        Path(sealed_dir).resolve(), Path(target_path).resolve(), Path(output_path))
    prediction, target = parse_ca(str(sealed_dir / "prediction.pdb")), parse_ca(str(target_path))
    count = min(len(prediction), len(target))
    prediction, target = prediction[:count], target[:count]
    pd = np.linalg.norm(prediction[:, None, :] - prediction[None, :, :], axis=2)
    td = np.linalg.norm(target[:, None, :] - target[None, :, :], axis=2)
    result = {
        "schema": "fold-protein-blind-evaluation/v30", "status": "completed",
        "result_type": "cumulative development benchmark", "official_run": False,
        "run_id": seal["run_id"], "execution": "post-seal structural comparison",
        "seal_sha256": sha(sealed_dir / "seal.json"),
        "target_id": target_path.name, "target_sha256": sha(target_path),
        "matched_ca_atoms": count, "sequence_length": len(states["sequence"]),
        "tm_score": float(compute_tm(prediction, target)),
        "ca_drmsd_angstrom": float(np.sqrt(np.mean((pd - td) ** 2))),
        "tertiary_path_edge_count": states["tertiary_census"]["path_edge_count"],
        "maximum_body_degree": max(states["tertiary_census"]["body_degrees"], default=0),
    }
    for name in ("v25", "v26_1", "v27", "v28"):
        result[name + "_departures"] = states[name + "_departures"]
    if output_path.exists():
        raise FileExistsError(output_path)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("sealed_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(
        args.manifest, args.sealed_dir, args.target, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
