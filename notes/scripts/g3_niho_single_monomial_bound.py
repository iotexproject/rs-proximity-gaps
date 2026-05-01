"""g3_niho_single_monomial_bound.py — for the α_2* mechanism, the
saturating-column condition reduces to:

  Q(p*, c): #{z ∈ L_2 : c·z^{p*} = a + b·z}  for some (a, b) ∈ F_q²

This is a Niho/Welch-Gong cross-correlation problem on L_2 = ⟨ω^4⟩.

For Pattern A 3-pos sparse with shared L_2 pos p*, fold²(α_1, α_2*) = c·z^{p*}
(constant in α_1). It's bad iff max-(a,b) Q(p*, c) ≥ n_2 - w_J_L2 = 4.

This script:
  1. Enumerates p* ∈ {0, 1, ..., n_2-1} = {0, ..., 7}
  2. For each c ∈ F_q*, computes Niho-max(c·z^{p*}) = max over (a, b) of Q.
  3. Reports for which (p*, c) the d_2 ≤ w_J_L2.

By Bezout, Q ≤ deg(c·z^{p*} - bz - a) = max(p*, 1). So upper bound = p*.
But empirically d_2 = w_J_L2 exactly when p* = "right" — the Niho phenomenon.
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, modinv
from mds_decoder import precompute_diff_inv, batched_extras


def main():
    p = 97
    n0, k0, R = 32, 8, 2
    n2, k2 = 8, 2
    w_J_L2 = 4

    chain = setup_chain(p, n0, k0, R=R)
    L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

    print(f"=== Niho-type single-monomial bound on L_2 (q={p}, n_2={n2}, k_2={k2}, w_J={w_J_L2}) ===")
    print(f"  L_2 = {L2}")

    # For each p* ∈ [0, n_2-1] and c ∈ F_q*, compute d_2(c·z^{p*}).
    print(f"\n  {'p*':<4} {'gcd(p*,n_2)':<12} {'agreement-distribution (over c ∈ F_q*)':<50}")
    print("  " + "-"*80)

    for pstar in range(n2):
        # Build single-monomial vector: at L_2[i], value = z^{p*} = L_2[i]^{p*}
        # Then check d_2 over c.
        agree_dist = Counter()
        agree_d2_dist = Counter()
        for c in range(1, p):
            # vec[i] = c · L_2[i]^{pstar}
            vec = [(c * pow(int(L2[i]), pstar, p)) % p for i in range(n2)]
            v_arr = np.array(vec, dtype=np.int64)
            extras = batched_extras(info_sets_n2, v_arr, L2_arr, D2, inv_D2, p)
            d2 = n2 - k2 - int(extras.max())
            agreement = n2 - d2  # = k_2 + max_extras
            agree_dist[agreement] += 1
            agree_d2_dist[d2] += 1
        gcd_val = math_gcd(pstar, n2) if pstar else n2
        ds = ', '.join(f"d_2={d}:{n}" for d, n in sorted(agree_d2_dist.items()))
        bad = sum(n for d, n in agree_d2_dist.items() if d <= w_J_L2)
        good = sum(n for d, n in agree_d2_dist.items() if d > w_J_L2)
        print(f"  {pstar:<4} {gcd_val:<12} {ds[:50]} | bad/total = {bad}/{p-1}")

    print(f"\n  Summary: which p* admit single-monomial c·z^{{p*}} with d_2 ≤ {w_J_L2}?")
    for pstar in range(n2):
        n_bad = 0
        for c in range(1, p):
            vec = [(c * pow(int(L2[i]), pstar, p)) % p for i in range(n2)]
            v_arr = np.array(vec, dtype=np.int64)
            extras = batched_extras(info_sets_n2, v_arr, L2_arr, D2, inv_D2, p)
            d2 = n2 - k2 - int(extras.max())
            if d2 <= w_J_L2: n_bad += 1
        ratio = n_bad / (p - 1)
        flag = "ALL bad ✓" if n_bad == p - 1 else (f"{n_bad}/{p-1} bad" if n_bad > 0 else "NEVER bad")
        print(f"    p* = {pstar}: {flag}  (ratio {ratio:.3f})")


def math_gcd(a, b):
    while b: a, b = b, a%b
    return a


if __name__ == "__main__":
    main()
