#!/usr/bin/env python3 -u
"""Phase 1 focused sweep: find c*(n, k=n/2) — smallest c where v3 bound holds.

For each (n, c) with k=n/2:
1. Run heavy random + targeted search across multiple primes
2. Take MAX max_bad over all (p, trial)
3. Compare to bound ⌊(2D-1)/c⌋
4. c* = smallest c where max_bad ≤ bound

This sweeps n ∈ {8, 12, 16, 20, 24} and c ∈ {2, ..., c_J+1}.
Output: CSV + summary.
"""

import sys, time
import numpy as np
from itertools import combinations, product
from math import comb

# Import shared helpers
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import (
    is_prime, primes_dividing_minus1, find_omega,
    elp, precompute_NE, count_bad_gammas
)

def heavy_search(NE, p, D, n_trials=50000, seed=0):
    """Heavy random search. Returns best max_bad found."""
    rng = np.random.default_rng(seed)
    best = 0
    for t in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        if not np.any(s2 != 0): continue
        m = count_bad_gammas(NE, s1, s2, p)
        if m > best:
            best = m
    return best

def targeted_search(NE, p, D, n_max=2):
    """Targeted: small-integer (s_1, s_2). Try sparse forms."""
    best = 0
    # Sparse s_1, s_2 with small entries
    for s1_pat in product(range(-n_max, n_max+1), repeat=min(D, 4)):
        for s2_pat in product(range(-n_max, n_max+1), repeat=min(D, 4)):
            s1 = np.zeros(D, dtype=np.int64)
            s2 = np.zeros(D, dtype=np.int64)
            s1[:len(s1_pat)] = s1_pat
            s2[:len(s2_pat)] = s2_pat
            s1 = s1 % p; s2 = s2 % p
            if not np.any(s2 != 0): continue
            m = count_bad_gammas(NE, s1, s2, p)
            if m > best:
                best = m
    return best

def run_nc(n, k, c, primes, n_trials=20000):
    """Run heavy search at all primes for (n, k, c). Return overall max."""
    D = n - k
    w = D - c
    if w < 1 or w >= n:
        return None
    nE = comb(n, w)
    if nE > 5_000_000:
        return None

    bound = (2*D - 1) // c
    overall_best = 0
    best_p = None

    for p in primes:
        omega = find_omega(n, p)
        if omega is None:
            continue
        L = [pow(omega, i, p) for i in range(n)]
        allE = list(combinations(range(n), w))
        NE = precompute_NE(allE, L, p, D, c)

        # Heavy random
        m_rand = heavy_search(NE, p, D, n_trials=n_trials, seed=42)
        # Targeted (only for small D)
        m_targ = targeted_search(NE, p, D, n_max=2) if D <= 8 else 0
        m = max(m_rand, m_targ)

        if m > overall_best:
            overall_best = m; best_p = p

    return {
        'n': n, 'k': k, 'c': c, 'D': D, 'w': w, 'nE': nE,
        'bound': bound, 'max_bad': overall_best, 'best_p': best_p,
    }

def main():
    import csv

    # Sweep
    configs = []
    for n in [8, 12, 16, 20, 24]:
        k = n // 2
        D = n - k
        # c_J approximately at rate 1/2
        c_J = max(1, n - k - int(n * (1 - (k/n)**0.5)))
        # Sweep c from 2 (since c=1 always fails) to c_J + 1
        for c in range(2, min(D, c_J + 2)):
            configs.append((n, k, c))

    print(f"Sweeping {len(configs)} configurations:")
    for cfg in configs:
        n, k, c = cfg
        D = n - k
        bound = (2*D - 1) // c
        print(f"  n={n} k={k} c={c} D={D} w={D-c} bound=⌊{2*D-1}/{c}⌋={bound}")
    print()

    out_path = 'notes/scripts/op2_cstar_results.csv'
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n', 'k', 'c', 'D', 'w', 'nE', 'bound', 'max_bad', 'best_p', 'pass_bound', 'time_s'])

        for (n, k, c) in configs:
            t0 = time.time()
            # Choose primes: a mix of small and large
            primes_small = primes_dividing_minus1(n, 11, 200)[:3]
            primes_med   = primes_dividing_minus1(n, 200, 1000)[:2]
            primes_large = primes_dividing_minus1(n, 1000, 5000)[:2]
            primes = sorted(set(primes_small + primes_med + primes_large))[:6]

            r = run_nc(n, k, c, primes, n_trials=20000)
            dt = time.time() - t0
            if r is None:
                print(f"  SKIP n={n} c={c}", flush=True)
                continue

            ok = r['max_bad'] <= r['bound']
            marker = 'PASS' if ok else 'FAIL'
            writer.writerow([r['n'], r['k'], r['c'], r['D'], r['w'], r['nE'],
                             r['bound'], r['max_bad'], r['best_p'],
                             marker, f'{dt:.1f}'])
            f.flush()
            print(f"  n={n:2d} c={c:2d}: max_bad={r['max_bad']:4d} bound={r['bound']:4d}  "
                  f"best_p={r['best_p']}  [{marker}]  {dt:.1f}s", flush=True)

    print(f"\nResults: {out_path}")

    # Summarize: for each n, find smallest c that passes
    print("\n=== c*(n, k=n/2) inferred ===")
    with open(out_path) as f:
        reader = csv.DictReader(f)
        by_n = {}
        for row in reader:
            n_, c_ = int(row['n']), int(row['c'])
            ok = row['pass_bound'] == 'PASS'
            by_n.setdefault(n_, []).append((c_, ok, int(row['max_bad']), int(row['bound'])))
    for n_, items in sorted(by_n.items()):
        items.sort()
        c_star = None
        for c_, ok, mb, b in items:
            if ok and c_star is None:
                c_star = c_
        print(f"  n={n_:2d}: c* = {c_star}  | by c: " +
              ', '.join(f'c={c_}:{mb}/{b}{"✓" if ok else "✗"}' for c_, ok, mb, b in items))

if __name__ == '__main__':
    main()
