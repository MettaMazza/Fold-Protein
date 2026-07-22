#!/usr/bin/env python3
"""Build the deterministic evidence bundle for the standalone Protein paper."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "zenodo"
BUNDLE = OUTPUT / "10_EVIDENCE_BUNDLE_Blind_Predictive_Super_Parity.zip"
MANIFEST = OUTPUT / "02_EVIDENCE_MANIFEST_Blind_Predictive_Super_Parity.json"

EXACT_FILES = [
    "README.md",
    "papers/From_One_Theorem_to_Blind_Protein_Structure_A_Zero_Parameter_Computational_Proof.md",
    "publication/EVIDENCE_README.md",
    "publication/zenodo_standalone_metadata_v1.json",
    "requirements-reproduction.txt",
    "calculate_tm.py",
    "tools/predict_structure.py",
    "constants/protein_folding_v2.ep",
    "constants/protein_window_orientation_v2.ep",
    "constants/protein_interwindow_orientation_v2.ep",
    "constants/protein_folding_3d_v2.ep",
    "constants/protein_material_architecture_v1_admission.ep",
    "constants/protein_blind_selector_v42_admission.ep",
    "constants/protein_blind_selector_v43_admission.ep",
    "constants/protein_blind_selector_v44_admission.ep",
    "constants/protein_blind_selector_v45_admission.ep",
    "tools/blind_24_lattice_selector_v3.py",
    "tools/analyze_protected_path_against_recovered_frontiers.py",
    "tools/derive_protein_material_relation_v1.py",
    "tools/protein_material_architecture_v1.py",
    "tools/register_protein_material_protocol_v1.py",
    "tools/run_protein_material_protocol_v1.py",
    "tools/verify_protein_material_architecture_v1.py",
    "tools/verify_protein_derivation_admission.py",
    "tools/verify_protein_forcing_registry.py",
    "verify/1ubq.pdb",
    "verify/1ubq_test_24_lattice.pdb",
    "verify/ubiquitin_24_lattice_manifest.json",
    "verify/replay_ubiquitin_24_lattice.py",
    "verify/protein_material_relation_v1.json",
    "verify/protein_material_architecture_v1_admission.json",
    "verify/protein_material_protocol_v1.json",
    "verify/protein_material_architecture_v1_applied_evidence.json",
    "verify/protected_path_recovered_frontier_comparison_v1.json",
    "verify/historical_positive_frontier_recovery_summary_v1.json",
    "verify/protein_selector_v35_generalisation_evidence_v1.json",
    "verify/blind_local_sequence_evidence_20260719.json",
    "verify/protein_forcing_registry_v1.json",
    "verify/protein_derivation_admission_v1.json",
    "verify/PROTEIN_FORCING_AUDIT.md",
    "verify/POSITIVE_CANDIDATE_PRESERVATION_AUDIT.md",
    "verify/evaluate_sealed_protein_material_v1.py",
    "verify/test_protein_folding_v2.c",
    "verify/test_protein_window_orientation_v2.c",
    "verify/test_protein_interwindow_orientation_v2.c",
    "verify/test_protein_folding_3d_v2.c",
    "verify/protein_angle_form_admission.c",
    "tests/test_protein_material_architecture_v1_admission.ep",
    "tests/test_protein_forcing_registry.py",
]

TREE_PATHS = [
    "verify/development_runs/ubiquitin_material_v1_complete_domain_l76_20260721_r2",
]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def collect() -> list[Path]:
    paths = [ROOT / item for item in EXACT_FILES]
    for tree in TREE_PATHS:
        paths.extend(path for path in (ROOT / tree).rglob("*") if path.is_file())
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("missing evidence files:\n" + "\n".join(missing))
    return sorted(set(paths), key=lambda path: path.relative_to(ROOT).as_posix())


def zip_info(relative: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(relative, date_time=(2026, 7, 22, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    return info


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = collect()
    entries = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        entries.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        })
    manifest = {
        "schema": "fold-protein-standalone-zenodo-evidence/v1",
        "title": "From One Self-Proven Theorem to Blind Protein Structure",
        "doi": "10.5281/zenodo.21482128",
        "author": "Maria Smith — Ernos Labs",
        "result": "Blind Predictive Super Parity",
        "headline_metrics": {
            "tm_repo": 0.9891211351471241,
            "ca_drmsd_angstrom": 0.2608575407959516,
            "kabsch_ca_rmsd_angstrom": 0.3261459535125402,
            "raw_state_trials": 43776,
            "states_per_residue": 576,
            "trained_weights": 0,
            "fitted_parameters": 0,
            "candidate_orderings": 0,
            "target_accesses": 0
        },
        "files": entries,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    MANIFEST.write_bytes(manifest_bytes)
    with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr(zip_info("EVIDENCE_MANIFEST.json"), manifest_bytes)
        for path in paths:
            relative = path.relative_to(ROOT).as_posix()
            archive.writestr(zip_info(relative), path.read_bytes())
    print(f"manifest={MANIFEST}")
    print(f"bundle={BUNDLE}")
    print(f"files={len(entries)}")
    print(f"bundle_sha256={digest(BUNDLE)}")


if __name__ == "__main__":
    main()
