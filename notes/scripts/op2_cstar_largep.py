#!/usr/bin/env python3 -u
"""Phase 1 v2: c*(n,k) at LARGE p only.

The v3 conjecture is about M_∞ (large-p limit), not peak. At small p,
max_bad can saturate to ≈p due to mod-p coincidence — these don't count
against the conjecture.

Strategy:
- For each (n, k, c): test at primes p with p > 100·⌊(2D-1)/c⌋, i.e.,
  p far above the bound (so saturation impossible).
- Run heavy random + targeted at each prime.
- Report per-prime data + aggregate.

c*(n,k) = smallest c such that max_bad ≤ ⌊(2D-1)/c⌋ at all tested large p.
"""

import sys, time
import numpy as np
from itertools import combinations
from math import comb
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import (
    is_prime, primes_dividing_minus1, find_omega,
    elp, precompute_NE, count_bad_gammas
)

def heavy_search(NE, p, D, n_trials, seed=0):
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

def run_nc_largep(n, k, c, n_trials_per_p=30000):
    """For (n,k,c), run at LARGE primes only (p >> bound)."""
    D = n - k
    w = D - c
    if w < 1 or w >= n:
        return None
    nE = comb(n, w)
    if nE > 5_000_000:
        return None

    bound = (2*D - 1) // c
    # Need p well above bound to avoid saturation
    p_floor = max(50, 20 * bound + 1)
    primes = primes_dividing_minus1(n, p_floor, 50000)
    if len(primes) < 3:
        # Try larger range
        primes = primes_dividing_minus1(n, p_floor, 200000)
    primes = primes[:5]  # take 5 large primes

    results = []
    for p in primes:
        omega = find_omega(n, p)
        if omega is None: continue
        L = [pow(omega, i, p) for i in range(n)]
        allE = list(combinations(range(n), w))
        NE = precompute_NE(allE, L, p, D, c)

        m = heavy_search(NE, p, D, n_trials=n_trials_per_p, seed=42)
        results.append((p, m))

    if not results:
        return None

    max_over_p = max(r[1] for r in results)
    return {
        'n': n, 'k': k, 'c': c, 'D': D, 'w': w, 'nE': nE,
        'bound': bound, 'max_bad': max_over_p,
        'per_prime': results,
        'pass': max_over_p <= bound,
    }

def main():
    import csv

    configs = []
    # Sweep at rate 1/2
    for n in [8, 12, 16, 20, 24]:
        k = n // 2
        D = n - k
        c_J = max(1, n - k - int(n * (1 - (k/n)**0.5)))
        for c in range(2, min(D, c_J + 2)):
            configs.append((n, k, c))

    print(f"Sweeping {len(configs)} configs at LARGE p:")
    out = 'notes/scripts/op2_cstar_largep_results.csv'
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n', 'k', 'c', 'D', 'w', 'nE', 'bound', 'max_bad',
                    'per_prime_results', 'pass', 'time_s'])

        for (n, k, c) in configs:
            t0 = time.time()
            r = run_nc_largep(n, k, c, n_trials_per_p=30000)
            dt = time.time() - t0
            if r is None:
                print(f"  SKIP n={n} c={c}", flush=True)
                continue
            pp_str = ';'.join(f'{p}:{m}' for p, m in r['per_prime'])
            marker = 'PASS' if r['pass'] else 'FAIL'
            w.writerow([r['n'], r['k'], r['c'], r['D'], r['w'], r['nE'],
                        r['bound'], r['max_bad'], pp_str, marker, f'{dt:.1f}'])
            f.flush()
            print(f"  n={n:2d} c={c:2d} D={r['D']} w={r['w']}: max={r['max_bad']:3d} bound={r['bound']:3d} "
                  f"[{marker}] per_p={pp_str}  {dt:.0f}s", flush=True)

    # Summarize: c*(n) = smallest passing c
    print("\n=== c*(n, k=n/2) inferred ===")
    with open(out) as f:
        reader = csv.DictReader(f)
        by_n = {}
        for row in reader:
            n_, c_ = int(row['n']), int(row['c'])
            ok = row['pass'] == 'PASS'
            by_n.setdefault(n_, []).append((c_, ok, int(row['max_bad']), int(row['bound'])))
    for n_, items in sorted(by_n.items()):
        items.sort()
        c_star = next((c_ for c_, ok, _, _ in items if ok), None)
        print(f"  n={n_:2d}: c* = {c_star}  | by c: " +
              ', '.join(f'c={c_}:{mb}/{b}{"✓" if ok else "✗"}' for c_, ok, mb, b in items))

if __name__ == '__main__':
    main()
