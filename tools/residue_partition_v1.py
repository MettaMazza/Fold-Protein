#!/usr/bin/env python3
"""Executable residue partition used by the blind-selector continuation.

This module makes the selector's registered biochemical classification a
complete constitutional input instead of leaving an unexplained string inside
the search code. It does not claim that the classification is newly proved by
the One: the engine decides admission from the registered route, while this
source proves the narrower computational facts that the alphabet is complete,
the classes are disjoint, and the selector receives exactly the sealed class.
"""
from __future__ import annotations


AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
HYDROPHOBIC_PACKING = frozenset("VILMFWCY")
OTHER_RESIDUES = AMINO_ACIDS - HYDROPHOBIC_PACKING

REGISTERED_PARTITION = {
    "hydrophobic_packing": HYDROPHOBIC_PACKING,
    "other": OTHER_RESIDUES,
}


def verify_registered_partition() -> dict:
    """Return the exhaustive partition census or halt on overlap/omission."""
    observed = set()
    for class_name, residues in REGISTERED_PARTITION.items():
        overlap = observed & residues
        if overlap:
            raise RuntimeError(
                f"registered residue classes overlap in {class_name}: "
                f"{''.join(sorted(overlap))}"
            )
        observed.update(residues)
    missing = AMINO_ACIDS - observed
    unexpected = observed - AMINO_ACIDS
    if missing or unexpected:
        raise RuntimeError(
            "registered residue partition does not close; "
            f"missing={''.join(sorted(missing))}; "
            f"unexpected={''.join(sorted(unexpected))}"
        )
    return {
        "alphabet": "".join(sorted(AMINO_ACIDS)),
        "alphabet_count": len(AMINO_ACIDS),
        "classes": {
            name: "".join(sorted(residues))
            for name, residues in REGISTERED_PARTITION.items()
        },
        "class_counts": {
            name: len(residues)
            for name, residues in REGISTERED_PARTITION.items()
        },
    }


PARTITION_CENSUS = verify_registered_partition()
