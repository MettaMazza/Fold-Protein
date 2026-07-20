#!/usr/bin/env python3
"""Weight-free symmetric balance under hierarchical hard exclusions.

The generated backbone is the parent assembly and attached side-chain graphs
are its children. Their absolute exclusions therefore form an ordered integer
vector rather than a commensurate sum: backbone exclusions are exhausted
first, followed by side-chain exclusions. Only within an identical hard vector
does the existing permutation-invariant symmetric ordinal balance act.
"""
from __future__ import annotations

from collections import defaultdict
import math


def _validate(candidates):
    rows = list(candidates)
    if not rows:
        return rows, 0, 0
    objective_dimension = len(rows[0][1])
    hard_dimension = len(rows[0][0])
    if objective_dimension < 1 or hard_dimension < 1:
        raise ValueError("hard and constitutional dimensions must be positive")
    seen = set()
    for hard, objectives, identity in rows:
        if (not isinstance(hard, tuple) or len(hard) != hard_dimension
                or any(not isinstance(value, int) or value < 0 for value in hard)):
            raise ValueError("hard exclusions must be a fixed non-negative integer tuple")
        if len(objectives) != objective_dimension:
            raise ValueError("constitutional objective dimensions do not close")
        if any(not math.isfinite(float(value)) for value in objectives):
            raise ValueError("constitutional objective must be finite")
        if identity in seen:
            raise ValueError("candidate identity is not unique")
        seen.add(identity)
    return rows, objective_dimension, hard_dimension


def symmetric_ordinal_vectors(candidates) -> dict[tuple, tuple[int, ...]]:
    rows, dimension, _ = _validate(candidates)
    if not rows:
        return {}
    rank_maps = []
    for axis in range(dimension):
        ordered = sorted({float(row[1][axis]) for row in rows})
        rank_maps.append({value: rank for rank, value in enumerate(ordered)})
    vectors = {}
    for _, objectives, identity in rows:
        ranks = [
            rank_maps[axis][float(objectives[axis])]
            for axis in range(dimension)]
        vectors[identity] = tuple(sorted(ranks, reverse=True))
    return vectors


def select_balanced_hierarchy(candidates, width: int,
                              include_boundary_ties=False):
    rows, _, _ = _validate(candidates)
    if not isinstance(width, int) or width < 1:
        raise ValueError("positive integer frontier width required")
    if len(rows) <= width:
        return sorted(rows, key=lambda row: (row[0], row[2]))
    strata = defaultdict(list)
    for row in rows:
        strata[row[0]].append(row)
    selected = []
    for hard in sorted(strata):
        stratum = strata[hard]
        remaining = width - len(selected)
        if remaining <= 0:
            break
        if len(stratum) <= remaining:
            selected.extend(sorted(stratum, key=lambda row: row[2]))
            continue
        vectors = symmetric_ordinal_vectors(stratum)
        ordered = sorted(stratum, key=lambda row: (vectors[row[2]], row[2]))
        if include_boundary_ties:
            boundary = vectors[ordered[remaining - 1][2]]
            selected.extend(row for row in ordered if vectors[row[2]] <= boundary)
        else:
            selected.extend(ordered[:remaining])
        break
    return selected
