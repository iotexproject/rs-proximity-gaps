#!/usr/bin/env python3 -u
"""Quick verify: c=3 at large p for n=20, n=24.

Just 2 primes per n, 30K trials per prime. Goal: confirm c=3 PASSES at
sufficiently large p.
"""

import sys, time
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import (
    primes_dividing_minus1, find_omega,
    elp, precompute_NE, count_bad_gammas
)

def heavy(NE, p, D, n_trials):
    rng = np.random.default_rng(42)
    best = 0
    for _ in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue
        m = count_bad_gammas(NE, s1, s2, p)
        if m > best:
            best = m
    return best

for n in [20, 24]:
    k = n // 2; D = n - k; c = 3; w = D - c
    bound = (2*D - 1) // c
    from math import comb
    nE = comb(n, w)
    print(f"\nn={n} k={k} c={c} D={D} w={w} bound={bound} nE={nE}")
    p_floor = 200 * bound
    primes = primes_dividing_minus1(n, p_floor, 50000)[:2]
    print(f"  primes: {primes}")
    for p in primes:
        t0 = time.time()
        omega = find_omega(n, p)
        if omega is None: continue
        L = [pow(omega, i, p) for i in range(n)]
        allE = list(combinations(range(n), w))
        NE = precompute_NE(allE, L, p, D, c)
        m = heavy(NE, p, D, 30000)
        dt = time.time() - t0
        marker = "FAIL" if m > bound else "PASS"
        print(f"  p={p:6d}  max_bad={m} [{marker}]  {dt:.0f}s", flush=True)
