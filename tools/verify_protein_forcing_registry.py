#!/usr/bin/env python3
"""Verify complete Fold Protein source classification and clean active closure."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verify.replay_protein_backbone_geometry_v1 import replay as replay_geometry
from tools.verify_blind_length_ladder_v2 import verify_ladder
from tools.verify_blind_panel_v2 import verify_panel


REGISTRY = ROOT / "verify/protein_forcing_registry_v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_scope() -> set[str]:
    paths = {
        "AGENT.md", "README.md", "calculate_tm.py",
        "verify/blind_selector_v1.json",
        "verify/blind_selector_v2.json",
        "verify/blind_selector_v2_length_ladder.json",
        "verify/blind_selector_v2_panel.json",
        "verify/blind_selector_v3.json",
        "verify/protein_backbone_geometry_v1.json",
        "verify/ubiquitin_24_lattice_manifest.json",
        "verify/test_protein_folding.c",
        "verify/test_protein_folding_3d.c",
    }
    for pattern in (
        "papers/*.md", "foundation/*.ep", "constants/*.ep", "tests/*.ep",
        "tests/*.py", "tools/*.py", "verify/*.py", "verify/*.md",
    ):
        paths.update(
            str(path.relative_to(ROOT)) for path in ROOT.glob(pattern) if path.is_file()
        )
    # The registry cannot contain its own hash/classification entry recursively.
    paths.discard("verify/protein_forcing_registry_v1.json")
    return paths


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def tracked_compiler_digest() -> tuple[int, str]:
    result = subprocess.run(
        ["git", "ls-files", "compiler"], cwd=ROOT,
        check=True, text=True, capture_output=True,
    )
    paths = [line for line in result.stdout.splitlines() if line]
    digest_input = bytearray()
    for relative in paths:
        file_hash = sha256(ROOT / relative)
        compiler_relative = relative.removeprefix("compiler/")
        digest_input.extend(f"{file_hash}  {compiler_relative}\n".encode())
    return len(paths), hashlib.sha256(digest_input).hexdigest()


def tracked_pdb_inventory() -> tuple[set[str], str]:
    result = subprocess.run(
        ["git", "ls-files", "*.pdb"], cwd=ROOT,
        check=True, text=True, capture_output=True,
    )
    paths = [line for line in result.stdout.splitlines() if line]
    digest_input = bytearray()
    for relative in paths:
        digest_input.extend(f"{sha256(ROOT / relative)}  {relative}\n".encode())
    return set(paths), hashlib.sha256(digest_input).hexdigest()


def verify_registry() -> dict:
    registry = json.loads(REGISTRY.read_text())
    if registry.get("schema") != "fold-protein-forcing-registry/v1":
        raise RuntimeError("unsupported protein forcing registry")

    classified = {}
    for class_name, paths in registry["classes"].items():
        for relative in paths:
            if relative in classified:
                raise RuntimeError(
                    f"source has multiple primary provenance classes: {relative}"
                )
            classified[relative] = class_name
    expected = source_scope()
    actual = set(classified)
    if expected != actual:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise RuntimeError(
            f"protein source coverage mismatch; missing={missing}; unexpected={unexpected}"
        )
    for relative in sorted(actual):
        if not (ROOT / relative).is_file():
            raise RuntimeError(f"classified protein source is missing: {relative}")

    compiler_boundary = registry["inherited_toolchain_boundary"]
    compiler_count, compiler_digest = tracked_compiler_digest()
    if compiler_count != compiler_boundary["tracked_files"]:
        raise RuntimeError("inherited compiler tracked-file census changed")
    if compiler_digest != compiler_boundary["tracked_file_set_sha256"]:
        raise RuntimeError("inherited compiler file-set digest changed")

    artifact_inventory = registry["artifact_inventory"]
    classified_artifacts = {}
    for class_name, paths in artifact_inventory["classes"].items():
        for relative in paths:
            if relative in classified_artifacts:
                raise RuntimeError(f"PDB has multiple artifact classes: {relative}")
            classified_artifacts[relative] = class_name
    tracked_pdbs, pdb_digest = tracked_pdb_inventory()
    if tracked_pdbs != set(classified_artifacts):
        raise RuntimeError(
            "tracked PDB coverage mismatch; "
            f"missing={sorted(tracked_pdbs - set(classified_artifacts))}; "
            f"unexpected={sorted(set(classified_artifacts) - tracked_pdbs)}"
        )
    if len(tracked_pdbs) != artifact_inventory["tracked_pdb_files"]:
        raise RuntimeError("tracked PDB census changed")
    if pdb_digest != artifact_inventory["tracked_pdb_file_set_sha256"]:
        raise RuntimeError("tracked PDB file-set digest changed")

    for relative, binding in registry["other_tracked_artifacts"].items():
        if sha256(ROOT / relative) != binding["sha256"]:
            raise RuntimeError(f"other tracked artifact drift: {relative}")

    legacy = set(registry["legacy_exclusion"]["forbidden_runtime_modules"])
    runtime_hashes = {}
    for selector in ("v3", "v5", "v8", "v9", "v10", "v11"):
        runtime_hashes[selector] = {}
        roots = registry["legacy_exclusion"][f"{selector}_runtime_roots"]
        for relative in roots:
            path = ROOT / relative
            imports = imported_modules(path)
            forbidden = sorted(imports & legacy)
            if forbidden:
                raise RuntimeError(
                    f"legacy runtime dependency entered selector-{selector}: "
                    f"{relative}: {forbidden}"
                )
            runtime_hashes[selector][relative] = sha256(path)

        manifest_path = ROOT / f"verify/blind_selector_{selector}.json"
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("legacy_runtime_imports") != []:
            raise RuntimeError(
                f"selector-{selector} manifest admits legacy runtime imports")
        for relative, expected_hash in manifest["source_sha256"].items():
            actual_hash = sha256(ROOT / relative)
            if actual_hash != expected_hash:
                raise RuntimeError(
                    f"selector-{selector} source drift: {relative}: "
                    f"{actual_hash} != {expected_hash}"
                )

    geometry = replay_geometry()
    if geometry.get("status") != "verified":
        raise RuntimeError("target-incapable geometry replay did not verify")
    ladder = verify_ladder(ROOT / "verify/blind_selector_v2_length_ladder_run_20260718")
    panel = verify_panel(ROOT / "verify/blind_selector_v2_panel_run_20260718")
    return {
        "schema": "fold-protein-forcing-registry-verification/v1",
        "status": "verified",
        "classified_sources": len(actual),
        "class_counts": {
            name: len(paths) for name, paths in registry["classes"].items()
        },
        "registry_sha256": sha256(REGISTRY),
        "v3_runtime_sha256": runtime_hashes,
        "geometry_replay": geometry,
        "history_floor_commit": registry["visible_history"]["first_commit"],
        "inherited_compiler": {
            "tracked_files": compiler_count,
            "tracked_file_set_sha256": compiler_digest,
        },
        "artifact_inventory": {
            "tracked_pdb_files": len(tracked_pdbs),
            "tracked_pdb_file_set_sha256": pdb_digest,
            "class_counts": {
                name: len(paths)
                for name, paths in artifact_inventory["classes"].items()
            },
            "v2_ladder": ladder,
            "v2_panel": panel,
        },
        "other_tracked_artifacts": len(registry["other_tracked_artifacts"]),
    }


if __name__ == "__main__":
    print(json.dumps(verify_registry(), sort_keys=True))
