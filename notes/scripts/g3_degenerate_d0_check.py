"""g3_degenerate_d0_check.py — for biquadratic supports with c_a=c_{a+16},
verify whether they are STRICT above-Johnson at level 0 (d_0 > 16) or only
at-Johnson (d_0 = 16).

Uses early-exit threshold (faster than exact d_0).
"""
import sys, os, math, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft_local(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def above_J_with_d0_lower(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p, batch_size=200000):
    """Return (above_J: bool, d0_upper_bound, max_extras_observed).
    Early-exit when max_extras >= n0-k0-w_J (then NOT above_J).
    """
    threshold = n0 - k0 - w_J  # need max_extras < threshold for above_J
    max_extras = 0
    all_T = list(combinations(range(n0), k0))
    total = len(all_T)
    seen = 0
    for start in range(0, total, batch_size):
        batch = all_T[start:start + batch_size]
        T_arr = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
        if max_extras >= threshold:
            return False, n0 - k0 - max_extras, max_extras
        seen += len(batch)
    return max_extras < threshold, n0 - k0 - max_extras, max_extras


def main():
    p = 1153
    n0, k0 = 32, 8
    w_J = n0 - int(math.isqrt(k0 * n0))  # = 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)

    print(f"=== d_0 above-J check at q={p}, ({n0},{k0}), w_J={w_J} ===")
    print(f"  d_0 > w_J ⟺ max_extras < {n0-k0-w_J} (over all C(32,8)=10518300 info sets)\n")

    # focus on degenerate coefs: c_a = c_{a+16}
    sups = [(8, 17, 24), (9, 16, 25), (10, 19, 26)]

    for sup in sups:
        a, b, c = sup
        coeffs_list = [
            ('all-1 (degenerate)', (1, 1, 1)),
            ('c_a=c_{a+16}=1, c_b=2 (deg)', (1, 2, 1)),
            ('c_a=c_{a+16}=3, c_b=5 (deg)', (3, 5, 3)),
            ('GENERIC (1, 1, 2)', (1, 1, 2)),
        ]
        for label, coeffs in coeffs_list:
            t0 = time.time()
            fhat = [0] * n0
            for ps, cc in zip(sup, coeffs):
                fhat[ps] = cc
            f = evaluate_dft_local(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            above, d0_ub, max_extras = above_J_with_d0_lower(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p)
            elapsed = time.time() - t0
            tag = "STRICT above-J" if above else f"NOT above-J (d_0 ≤ {d0_ub})"
            print(f"  sup={sup} coeffs={coeffs} [{label}]: max_extras={max_extras}, {tag}  [{elapsed:.0f}s]")
        print()


if __name__ == "__main__":
    main()
