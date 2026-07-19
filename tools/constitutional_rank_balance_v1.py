#!/usr/bin/env python3
"""Weight-free symmetric ordinal balance for constitutional relations.

Each relation orders candidates but contributes no commensurate numerical
scale.  Converting every objective to its within-frontier ordinal rank removes
units and magnitude.  Sorting each candidate's rank tuple from worst to best
then compares the worst rank first, followed by the next worst, and so on.
The result is invariant to objective permutation and strictly increasing
re-expression of any objective.  Hard exclusions remain separate strata and
are exhausted in ascending order before any softer relation is considered.
"""
from __future__ import annotations

from collections import defaultdict
import math


def _validate(candidates):
    rows = list(candidates)
    if not rows:
        return rows, 0
    dimension = len(rows[0][1])
    if dimension < 1:
        raise ValueError("at least one constitutional objective is required")
    seen = set()
    for hard, objectives, identity in rows:
        if not isinstance(hard, int) or hard < 0:
            raise ValueError("hard exclusion count must be a non-negative integer")
        if len(objectives) != dimension:
            raise ValueError("constitutional objective dimensions do not close")
        if any(not math.isfinite(float(value)) for value in objectives):
            raise ValueError("constitutional objective must be finite")
        if identity in seen:
            raise ValueError("candidate identity is not unique")
        seen.add(identity)
    return rows, dimension


def symmetric_ordinal_vectors(candidates) -> dict[tuple, tuple[int, ...]]:
    """Return permutation-invariant worst-first rank vectors by identity."""
    rows, dimension = _validate(candidates)
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
            for axis in range(dimension)
        ]
        vectors[identity] = tuple(sorted(ranks, reverse=True))
    return vectors


def select_balanced(candidates, width: int, include_boundary_ties=False):
    """Select by hard strata then symmetric ordinal minimax balance."""
    rows, _ = _validate(candidates)
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
        ordered = sorted(
            stratum, key=lambda row: (vectors[row[2]], row[2]))
        if include_boundary_ties:
            boundary = vectors[ordered[remaining - 1][2]]
            selected.extend(
                row for row in ordered if vectors[row[2]] <= boundary)
        else:
            selected.extend(ordered[:remaining])
        break
    return selected
