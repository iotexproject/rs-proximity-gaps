"""Shared utilities for paper2 L3 deployment-scale verification scripts.

Stdlib-only mod-p linear algebra and subgroup helpers.  Extracted from
the project notes/scripts/ to make this directory self-contained.
"""

from __future__ import annotations

import random
from collections import Counter


# ----------------------- field utilities -----------------------

def find_prim_root(p: int, n: int):
    if (p - 1) % n != 0:
        return None
    factors = set()
    t = n
    for q in range(2, n + 1):
        while t % q == 0:
            factors.add(q)
            t //= q
        if t == 1:
            break
    for g in range(2, p):
        w = pow(g, (p - 1) // n, p)
        if pow(w, n, p) != 1:
            continue
        if all(pow(w, n // q, p) != 1 for q in factors):
            return w
    return None


def modinv(a: int, p: int) -> int:
    return pow(a % p, p - 2, p)


def subgroup(n, p):
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError(f"F_{p} has no primitive {n}-th root")
    return [pow(omega, i, p) for i in range(n)]


# ----------------------- mod-p linear algebra -----------------------

def rank_mod_p(matrix, p):
    rows = [list(row) for row in matrix]
    nrows = len(rows)
    if nrows == 0:
        return 0
    ncols = len(rows[0])
    rank = 0
    col = 0
    while rank < nrows and col < ncols:
        pivot = None
        for i in range(rank, nrows):
            if rows[i][col] % p:
                pivot = i
                break
        if pivot is None:
            col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], p - 2, p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for i in range(nrows):
            if i != rank and rows[i][col] % p:
                f = rows[i][col]
                rows[i] = [(a - f * b) % p for a, b in zip(rows[i], rows[rank])]
        rank += 1
        col += 1
    return rank


def kernel_mod_p(matrix, p):
    """Return one nontrivial c with sum c_i row_i = 0, or None."""
    nrows = len(matrix)
    ncols = len(matrix[0])
    AT = [[matrix[i][j] for i in range(nrows)] for j in range(ncols)]
    rows = [list(r) for r in AT]
    n = len(rows)
    m = len(rows[0]) if rows else 0
    pivot_cols = []
    rank = 0
    col = 0
    pivot_for_col = [-1] * m
    while rank < n and col < m:
        pivot = None
        for i in range(rank, n):
            if rows[i][col] % p:
                pivot = i
                break
        if pivot is None:
            col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], p - 2, p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for i in range(n):
            if i != rank and rows[i][col] % p:
                f = rows[i][col]
                rows[i] = [(a - f * b) % p for a, b in zip(rows[i], rows[rank])]
        pivot_cols.append(col)
        pivot_for_col[col] = rank
        rank += 1
        col += 1
    free_cols = [c for c in range(m) if pivot_for_col[c] == -1]
    if not free_cols:
        return None
    fc = free_cols[0]
    c = [0] * m
    c[fc] = 1
    for pc in pivot_cols:
        r = pivot_for_col[pc]
        c[pc] = (-rows[r][fc]) % p
    return c


def sample_no_full_S(n2, k2, num_samples, seed=42):
    """Sample no-full sparse S subsets at L_2 = (n2, k2)."""
    rng = random.Random(seed)
    samples = set()
    half = n2 // 2
    attempts = 0
    while len(samples) < num_samples and attempts < num_samples * 100:
        attempts += 1
        S = tuple(sorted(rng.sample(range(n2), half)))
        counts = Counter(s % 4 for s in S)
        if max(counts.values()) >= k2:
            continue
        samples.add(S)
    return list(samples)
