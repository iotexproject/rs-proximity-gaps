#!/usr/bin/env python3 -u
"""D1 — extrapolation check for Note 0115.

Test whether `dim V_tet_sub(V) = 2(w'+1)` (Note 0114) holds at one
decade beyond the previous sweep: n ∈ {32, 40, 48, 64}.

For each (n, c), pick the smallest bad-realizing w' (the V_bad
bottleneck candidate) and run the density-in-span method. If the
formula holds, the conjectural codim formula in Note 0115 is
empirically supported through n = 64.
"""

import sys, math
import numpy as np
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_v_tet_sub_dim_general import (
    bad_realizing_X_dim, build_span, is_in_v_tet_sub
)


def smallest_bad_realizing_w_prime(D: int, c: int) -> int | None:
    """Smallest w' with X_dim ≥ 1 AND w' ≥ T (sub-tet realizes M > T)."""
    w = D - c
    T = (2 * D - 1) // c
    for wp in range(max(2, T), w + 1):
        if bad_realizing_X_dim(wp, w, c) >= 1:
            return wp
    return None


def measure(n: int, c: int, w_prime: int, p: int,
            n_gammas: int = 150, n_samples: int = 1000):
    D = n - n // 2; w = D - c
    m = w_prime + 1
    extras_size = w - w_prime
    omega = find_omega(n, p)
    if omega is None:
        return None
    L = [pow(omega, i, p) for i in range(n)]

    V = list(range(m))
    # Use SHARED extras across all supports — V_tet_sub depends only on V
    # (Note 0114 geometric argument).
    if extras_size > 0:
        U_shared = list(range(m, m + extras_size))
        if m + extras_size > n:
            return None
    else:
        U_shared = []

    Es = []
    for i in range(m):
        E_i = tuple(sorted(set(V) - {V[i]} | set(U_shared)))
        if V[i] in E_i: return None
        if len(E_i) != w: return None
        Es.append(E_i)
    NEs = make_NEs(Es, L, p, D, c, w)

    print(f"  building span (m={m}, c={c}, n_gammas={n_gammas})...", flush=True)
    basis = build_span(NEs, p, D, c, m, n_gammas=n_gammas)
    D_span = basis.shape[0]
    if D_span == 0:
        return {'D_span': 0, 'density': 0, 'dim_est': float('-inf'),
                'predicted': 2 * m, 'p': p}

    print(f"  sampling {n_samples} points...", flush=True)
    rng = np.random.default_rng(123)
    n_in = 0
    for trial in range(n_samples):
        coefs = rng.integers(0, p, D_span)
        v = (coefs @ basis) % p
        s1 = v[:D]; s2 = v[D:]
        in_v, _ = is_in_v_tet_sub(s1, s2, NEs, p, c)
        if in_v: n_in += 1
    density = n_in / n_samples
    log_p_density = (math.log(max(density, 1e-12)) / math.log(p)
                     if density > 0 else float('-inf'))
    dim_est = D_span + log_p_density if density > 0 else float('-inf')
    return {
        'D_span': D_span, 'in_v': n_in, 'n_samples': n_samples,
        'density': density, 'dim_est': dim_est,
        'predicted': 2 * m, 'p': p,
    }


def main():
    primes_priority = [1009, 449, 257, 193, 97, 41]
    cases = [
        # (n, c)
        (32, 3),  # D=16, T=10, w=13
        (32, 4),  # D=16, T=7,  w=12
        (40, 4),  # D=20, T=9,  w=16
        (48, 5),  # D=24, T=9,  w=19
        (64, 4),  # D=32, T=15, w=28
    ]
    print("=== D1 extrapolation: dim V_tet_sub at n ∈ {32, 40, 48, 64} ===")
    print(f"{'n':>3} {'c':>3} {'w':>3} {'T':>3} {'wp_min':>7} "
          f"{'pred':>5} {'D_span':>7} {'in/N':>10} {'dim_est':>9} "
          f"{'verdict':>10}")
    for n, c in cases:
        D = n - n // 2; w = D - c; T = (2 * D - 1) // c
        wpm = smallest_bad_realizing_w_prime(D, c)
        if wpm is None:
            print(f"{n:>3} {c:>3} {w:>3} {T:>3} (no bad-realizing w')")
            continue
        p = next((q for q in primes_priority if (q - 1) % n == 0), None)
        if p is None:
            print(f"{n:>3} {c:>3} {w:>3} {T:>3} (no prime)")
            continue
        print(f"\n[case n={n} c={c} w'_min={wpm} p={p}]", flush=True)
        result = measure(n, c, wpm, p)
        if result is None:
            print("  (build failed)")
            continue
        pred = result['predicted']
        if result['density'] == 0:
            verdict = 'EMPTY'
        elif abs(result['dim_est'] - pred) < 1.0:
            verdict = 'match'
        else:
            verdict = 'MISMATCH'
        print(f"{n:>3} {c:>3} {w:>3} {T:>3} {wpm:>7} {pred:>5} "
              f"{result['D_span']:>7} "
              f"{result['in_v']:>4}/{result['n_samples']:>3} "
              f"{result['dim_est']:>9.3f} "
              f"{verdict:>10}")


if __name__ == '__main__':
    main()
