#!/usr/bin/env python3
"""Compile and execute the source-bound Protein engine closure receipts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verify/protein_engine_closure_v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_and_run(source: Path, binary: Path) -> subprocess.CompletedProcess[str]:
    subprocess.run(
        ["clang", str(source), "-O2", "-o", str(binary)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return subprocess.run(
        [str(binary)], cwd=ROOT, check=False, text=True, capture_output=True
    )


def verify_engine_closure() -> dict:
    receipt = json.loads(RECEIPT.read_text())
    if receipt.get("schema") != "fold-protein-engine-closure/v1":
        raise RuntimeError("unsupported Protein engine closure schema")

    for relative, expected in receipt["source_sha256"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise RuntimeError(
                f"Protein engine closure source drift: {relative}: {actual} != {expected}"
            )

    expected_markers = {
        "verify/test_protein_folding_v2.c": (
            "the One is the unique fixed point across both exact fold branches",
            "declared 3/4 query reaches the One in two exact folds",
        ),
        "verify/test_protein_window_orientation_v2.c": (
            "complete overlap space has one candidate with One advance",
        ),
        "verify/test_protein_interwindow_orientation_v2.c": (
            "complete quartet-overlap space has one candidate with One advance",
        ),
        "verify/test_protein_folding_3d_v2.c": (
            "canonical angle forms pass the engine admission guard",
        ),
        "verify/protein_angle_form_admission.c": (
            "all four canonical angle forms are uniquely admitted",
        ),
    }

    executed = {}
    with tempfile.TemporaryDirectory(prefix="fold-protein-engine-closure-") as temp:
        temp_path = Path(temp)
        for index, relative in enumerate(receipt["executables"]["passing"]):
            result = compile_and_run(ROOT / relative, temp_path / f"pass-{index}")
            if result.returncode != 0:
                raise RuntimeError(
                    f"Protein engine closure executable failed: {relative}: "
                    f"{result.stdout}{result.stderr}"
                )
            for marker in expected_markers[relative]:
                if marker not in result.stdout:
                    raise RuntimeError(
                        f"Protein engine closure output missing marker: {relative}: {marker}"
                    )
            executed[relative] = result.returncode

    angle = receipt["closed_relations"]["canonical_angle_forms"]
    if angle["complete_candidate_counts"] != {
        "homochiral_chart_sign": 1,
        "opposite_chart_sign": 1,
        "right_handed_alpha_phi": 1,
        "right_handed_alpha_psi": 1,
        "beta_phi": 1,
        "beta_psi": 1,
    }:
        raise RuntimeError("canonical-angle complete candidate census changed")

    homochirality = receipt["main_corpus_dependencies"]["constants/homochirality.ep"]
    if homochirality["sha256"] != "c00d45924978e4fdff114d3e30bd67754b9b55d52e8b467ef76b2f9fca8c2a5c":
        raise RuntimeError("main-corpus homochirality dependency binding changed")
    canonical_homochirality = ROOT.parent / "Smithian Fold Theory/constants/homochirality.ep"
    if canonical_homochirality.is_file():
        if sha256(canonical_homochirality) != homochirality["sha256"]:
            raise RuntimeError("local main-corpus homochirality source differs from the bound dependency")

    return {
        "schema": "fold-protein-engine-closure-verification/v1",
        "status": "verified",
        "closed_relations": sorted(receipt["closed_relations"]),
        "executed": executed,
        "angle_candidate_counts": angle["complete_candidate_counts"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_engine_closure(), sort_keys=True))
