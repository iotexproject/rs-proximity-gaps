"""g3_count_q_d0_check.py — for newly-discovered count=q witnesses in {16..23},
verify at-Johnson (d_0 <= 16) vs strict above-J.
"""
import sys, os, math, time, random
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
    threshold = n0 - k0 - w_J
    max_extras = 0
    all_T = list(combinations(range(n0), k0))
    for start in range(0, len(all_T), batch_size):
        batch = all_T[start:start + batch_size]
        T_arr = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
        if max_extras >= threshold:
            return False, n0 - k0 - max_extras, max_extras
    return max_extras < threshold, n0 - k0 - max_extras, max_extras


def main():
    p = 1153
    n0, k0 = 32, 8
    w_J = n0 - int(math.isqrt(k0 * n0))  # 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)

    print(f"=== d_0 above-J check on count=q witnesses in {{16..23}} ===\n")

    sups = [
        (16, 17, 19),
        (16, 17, 23),
        (17, 18, 19),
        (19, 20, 23),
        (21, 22, 23),
    ]

    rng = random.Random(2026)
    for sup in sups:
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        t0 = time.time()
        fhat = [0] * n0
        for ps, cc in zip(sup, coeffs):
            fhat[ps] = cc
        f = evaluate_dft_local(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)
        above, d0_ub, max_extras = above_J_with_d0_lower(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p)
        elapsed = time.time() - t0
        tag = "STRICT above-J" if above else f"NOT above-J (d_0 <= {d0_ub})"
        print(f"  sup={sup} coeffs={coeffs}: max_extras={max_extras}, {tag}  [{elapsed:.0f}s]")


if __name__ == "__main__":
    main()
