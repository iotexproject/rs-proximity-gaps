#!/usr/bin/env python3 -u
"""Focused test: c=3 at VERY large p (p in thousands) to verify whether
M_∞ ≤ ⌊(2D-1)/3⌋ or structurally exceeds it.

For each n ∈ {12, 16, 20, 24}: test c=3 at p ≈ 1000-5000 (much larger than bound).
If max_bad stays ≤ bound: lemma probably holds at c=3.
If max_bad stays > bound: structural failure at c=3, c*(n) > 3.
"""

import sys, time
import numpy as np
from itertools import combinations
from math import comb
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import (
    primes_dividing_minus1, find_omega,
    elp, precompute_NE, count_bad_gammas
)

def heavy_search(NE, p, D, n_trials=100000, seed=42):
    rng = np.random.default_rng(seed)
    best = 0
    for _ in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue
        m = count_bad_gammas(NE, s1, s2, p)
        if m > best:
            best = m
    return best

def run_n(n, c=3, n_trials=80000):
    k = n // 2
    D = n - k
    w = D - c
    if w < 1: return None
    nE = comb(n, w)
    bound = (2*D - 1) // c

    # VERY large primes: at least 100 × bound, prefer 1000+
    p_floor = max(500, 200 * bound)
    primes = primes_dividing_minus1(n, p_floor, 50000)[:5]
    if len(primes) < 3:
        primes = primes_dividing_minus1(n, p_floor, 200000)[:5]

    print(f"n={n} c={c}: D={D} w={w} bound={bound} nE={nE}")
    print(f"  testing primes: {primes}")
    results = []
    for p in primes:
        t0 = time.time()
        omega = find_omega(n, p)
        if omega is None: continue
        L = [pow(omega, i, p) for i in range(n)]
        allE = list(combinations(range(n), w))
        NE = precompute_NE(allE, L, p, D, c)
        m = heavy_search(NE, p, D, n_trials=n_trials, seed=42)
        dt = time.time() - t0
        results.append((p, m, dt))
        marker = "FAIL" if m > bound else "PASS"
        print(f"  p={p:6d}  max_bad={m:4d} bound={bound}  [{marker}]  {dt:.1f}s", flush=True)

    max_over = max(r[1] for r in results)
    consensus = "STRUCTURAL FAIL" if max_over > bound else "PASS at large p"
    print(f"  → {consensus}: max={max_over}, bound={bound}")
    return results

if __name__ == '__main__':
    print("=" * 60)
    print("Testing c=3 at VERY large p (p > 200·bound)")
    print("=" * 60)
    for n in [12, 16, 20, 24]:
        print()
        run_n(n, c=3, n_trials=80000)
