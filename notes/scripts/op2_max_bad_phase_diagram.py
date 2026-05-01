#!/usr/bin/env python3 -u
"""Phase 1 main sweep: find c*(n,k) — the transition where max_bad drops from
exponential (in n) to bounded by ⌊(2D-1)/c⌋.

For each (n, k, c): scan multiple primes p, run random (s_1, s_2) trials per p,
compute max_bad. Output CSV.

Key questions:
1. At each c, is max_bad polynomial or exponential in n?
2. Where does the transition happen — is c* = O(log n), O(√n), or Θ(n)?

Algorithm per (n, k, c, p, s_1, s_2):
  D = n - k
  w = D - c
  For each E ∈ C([n], w):
    N_E = c × D matrix (cols = error-locator polynomial coeffs of supp E)
    a_E = N_E · s_2    (c-vector)
    b_E = N_E · s_1    (c-vector)
    if a_E ∝ b_E (proportional):
      γ_E = -b_E[i]/a_E[i] for any i with a_E[i] ≠ 0
  max_bad = #{distinct γ_E values}
"""

import sys, time
import numpy as np
from itertools import combinations
from math import comb
import argparse

# ============ Number theory helpers ============

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    for d in range(3, int(n**0.5)+1, 2):
        if n % d == 0: return False
    return True

def primes_dividing_minus1(n, lo, hi):
    """Primes p in [lo, hi] with n | (p-1) (so L = ⟨ω_n⟩ ⊂ F_p^*)."""
    return [p for p in range(lo, hi) if is_prime(p) and (p - 1) % n == 0]

def find_omega(n, p):
    """Find primitive n-th root of unity in F_p."""
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        omega = pow(g, (p - 1) // n, p)
        if pow(omega, n, p) == 1:
            ok = all(pow(omega, d, p) != 1 for d in range(1, n) if d < n and n % d == 0)
            if ok:
                return omega
    return None

# ============ Error-locator polynomial ============

def elp(E, L, p):
    """Coefficients of ∏_{i ∈ E} (z - L[i]) modulo p."""
    c = [1]
    for i in E:
        r = L[i]
        new = [0] * (len(c) + 1)
        for j, v in enumerate(c):
            new[j+1] = (new[j+1] + v) % p
            new[j]   = (new[j]   - r * v) % p
        c = new
    return [x % p for x in c]

def precompute_E_matrices(n, k, p, L):
    """For each E ∈ C([n], w), precompute the c × D matrix N_E
    whose rows are translated ELP coefficients.

    N_E[r, j] = lam[j-r]  for 0 ≤ r < c, 0 ≤ j < D, with lam coefficients
    of error-locator polynomial of E. (Block Toeplitz of ELP, c rows.)
    """
    D = n - k; w = D - c_excess(n, k, p, D)  # placeholder, fixed per call
    # We pass c_excess explicitly via the wrapping run() function, so this
    # helper is only used in run() with explicit (c, w).
    raise RuntimeError("use precompute_NE inside run() instead")

def c_excess(n, k, p, D):
    return None  # not used

# ============ Core computation ============

def precompute_NE(allE, L, p, D, c):
    """For each support E (size w = D - c), build the c × D matrix N_E.
    Returns NE shape (nE, c, D).
    """
    w = D - c
    nE = len(allE)
    NE = np.zeros((nE, c, D), dtype=np.int64)
    for idx, E in enumerate(allE):
        lam = elp(E, L, p)  # length w + 1
        # The c-dim orthogonal complement of V_E (Vandermonde restricted to E)
        # is spanned by shifted ELP coefficient vectors:
        #   N[r, j] = lam[j - r]  for 0 ≤ r < c
        # (where lam[t] = 0 for t < 0 or t > w)
        for r in range(c):
            for j in range(D):
                t = j - r
                if 0 <= t <= w:
                    NE[idx, r, j] = lam[t] % p
    return NE

def count_bad_gammas(NE, s1, s2, p):
    """Given precomputed N_E for all E and (s_1, s_2), return #distinct γ
    values such that ∃ E with line s_1 + γs_2 inside V_E.

    Condition for E to contribute γ:
      a_E = N_E · s_2  ∈ F_p^c
      b_E = N_E · s_1  ∈ F_p^c
      a_E and b_E proportional, with a_E ≠ 0 → γ = -b_E[i] / a_E[i]
    """
    nE, c, D = NE.shape
    # Compute aE, bE for all E in batch
    aE = (NE @ s2) % p   # shape (nE, c)
    bE = (NE @ s1) % p   # shape (nE, c)

    # For c=1: condition is "a_E ≠ 0", γ = -b_E / a_E
    # For c>1: condition is a_E ∝ b_E, i.e., a_E[i] b_E[j] = a_E[j] b_E[i]
    #   for all i, j. Equivalent to det of every 2x2 minor = 0.
    # Equivalent characterization: rank([a_E; b_E]) ≤ 1.

    if c == 1:
        # a_E shape (nE, 1)
        a_flat = aE[:, 0]
        b_flat = bE[:, 0]
        valid = (a_flat != 0)
        if not np.any(valid):
            return 0
        a_inv = np.zeros(nE, dtype=np.int64)
        # Vectorized modular inverse via Fermat (small p)
        a_inv[valid] = pow_mod_vec(a_flat[valid], p - 2, p)
        gammas = (-b_flat[valid] * a_inv[valid]) % p
        return int(np.unique(gammas).size)

    # c ≥ 2: check a_E ∝ b_E using cross products (a_E[i] b_E[j] - a_E[j] b_E[i] = 0 for all i<j)
    # Use first nonzero coordinate of a_E to define γ
    # Compatibility: for all (i, j), a_E[i] * b_E[j] - a_E[j] * b_E[i] = 0 mod p

    # Build cross product matrix: cross[E, i, j] = a[i]*b[j] - a[j]*b[i]
    # Compatible if all cross[E, :, :] = 0
    # Vectorized: outer[E, i, j] = a[E, i] * b[E, j]
    outer_ab = (aE[:, :, None] * bE[:, None, :]) % p  # (nE, c, c)
    outer_ba = (aE[:, None, :] * bE[:, :, None]) % p  # (nE, c, c)
    cross = (outer_ab - outer_ba) % p
    # Compatible: all cross entries = 0
    compatible = np.all(cross == 0, axis=(1, 2))

    if not np.any(compatible):
        return 0

    # Among compatible, find first nonzero coord of aE to compute γ
    aE_c = aE[compatible]; bE_c = bE[compatible]
    nonzero_mask = (aE_c != 0)
    has_nz = np.any(nonzero_mask, axis=1)
    if not np.any(has_nz):
        return 0
    aE_c = aE_c[has_nz]; bE_c = bE_c[has_nz]
    nonzero_mask = nonzero_mask[has_nz]
    first_nz = np.argmax(nonzero_mask, axis=1)  # first True
    n_compat = aE_c.shape[0]
    rows = np.arange(n_compat)
    a_first = aE_c[rows, first_nz]
    b_first = bE_c[rows, first_nz]
    a_inv = pow_mod_vec(a_first, p - 2, p)
    gammas = (-b_first * a_inv) % p
    return int(np.unique(gammas).size)

def pow_mod_vec(base, exp, p):
    """Vectorized modular exponentiation using binary expansion."""
    result = np.ones_like(base)
    base = base.copy() % p
    e = exp
    while e > 0:
        if e & 1:
            result = (result * base) % p
        base = (base * base) % p
        e >>= 1
    return result

# ============ Trial driver ============

def run_config(n, k, c, p, n_trials=1000, rng_seed=42):
    """For one (n, k, c, p), run random (s_1, s_2) trials and return max_bad."""
    D = n - k
    w = D - c
    if w < 1 or w >= n:
        return None  # invalid

    omega = find_omega(n, p)
    if omega is None:
        return None
    L = [pow(omega, i, p) for i in range(n)]

    nE = comb(n, w)
    if nE > 5_000_000:
        # too large to enumerate; skip for now
        return {'skipped': True, 'reason': f'C({n},{w}) = {nE} too large'}

    allE = list(combinations(range(n), w))
    NE = precompute_NE(allE, L, p, D, c)

    rng = np.random.default_rng(rng_seed)
    best = 0
    for _ in range(n_trials):
        s1 = rng.integers(0, p, size=D, dtype=np.int64)
        s2 = rng.integers(0, p, size=D, dtype=np.int64)
        # require s_2 ≠ 0
        if not np.any(s2 != 0):
            continue
        m = count_bad_gammas(NE, s1, s2, p)
        if m > best:
            best = m
    return {'max_bad': best, 'nE': nE, 'p': p}

def run_sweep(out_csv, configs, n_trials=1000, primes_per_n=4):
    """Run the full sweep.
    configs: list of (n, k, c) tuples to test.
    """
    import csv
    rows = []

    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n', 'k', 'c', 'p', 'D', 'w', 'nE',
                         'max_bad', 'bound_2D-1_over_c', 'bound_C(n,w)',
                         'ratio_to_bound', 'time_s'])

        for (n, k, c) in configs:
            D = n - k
            w = D - c
            if w < 1 or w >= n:
                continue
            nE = comb(n, w)
            if nE > 5_000_000:
                print(f"SKIP (n,k,c)=({n},{k},{c}): C({n},{w}) = {nE} too large", flush=True)
                continue

            bound_2D = (2*D - 1) // c
            bound_full = nE  # binom(n, w)

            # Choose primes: a few small primes near saturation, plus some larger
            # First find primes p with n | p-1
            target_primes = []
            for plo, phi in [(11, 100), (100, 500), (500, 2000)]:
                cands = primes_dividing_minus1(n, plo, phi)
                if cands:
                    target_primes.append(cands[0])
            target_primes = sorted(set(target_primes))[:primes_per_n]

            for p in target_primes:
                t0 = time.time()
                r = run_config(n, k, c, p, n_trials=n_trials)
                dt = time.time() - t0
                if r is None or r.get('skipped'):
                    continue
                max_bad = r['max_bad']
                ratio = max_bad / max(1, bound_2D)
                writer.writerow([n, k, c, p, D, w, nE,
                                 max_bad, bound_2D, bound_full,
                                 f'{ratio:.3f}', f'{dt:.1f}'])
                f.flush()
                marker = '>BOUND' if max_bad > bound_2D else '≤BOUND'
                print(f"  n={n:2d} k={k:2d} c={c:2d} (D={D},w={w}) p={p:5d} "
                      f"max_bad={max_bad:6d} ⌊(2D-1)/c⌋={bound_2D:5d} "
                      f"C(n,w)={nE:8d} ratio={ratio:.2f} {marker}  {dt:.1f}s",
                      flush=True)

# ============ Main ============

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='notes/scripts/op2_phase_diagram.csv')
    ap.add_argument('--n_trials', type=int, default=200)
    ap.add_argument('--small', action='store_true', help='small smoke test only')
    args = ap.parse_args()

    if args.small:
        # smoke: small range
        configs = []
        for n in [12, 16, 20]:
            k = n // 2
            D = n - k
            for c in range(1, min(D, 5)):
                configs.append((n, k, c))
    else:
        # full sweep — n up to 24 (full enum), various rates
        configs = []
        for n in [12, 16, 20, 24]:
            for k_frac in [n // 4, n // 3, n // 2]:
                k = k_frac
                if k < 2 or k > n - 2:
                    continue
                D = n - k
                # c_J approximately at Johnson bound: c ≈ rate-dependent
                c_J = max(1, n - k - int(n * (1 - (k/n)**0.5)))  # approximate
                # sweep c from 1 to c_J + 1
                for c in range(1, min(D, c_J + 2)):
                    configs.append((n, k, c))

        # dedupe
        configs = sorted(set(configs))

    print(f"Running {len(configs)} configurations:")
    for cfg in configs:
        print(f"  (n,k,c) = {cfg}")
    print()

    t0 = time.time()
    run_sweep(args.out, configs, n_trials=args.n_trials)
    dt = time.time() - t0
    print(f"\nTotal: {dt:.1f}s. Output: {args.out}")

if __name__ == '__main__':
    main()
