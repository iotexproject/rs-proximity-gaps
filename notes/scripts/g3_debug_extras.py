"""g3_debug_extras.py — manual check of batched_extras at (64, 16)."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def lagrange_eval(xs, ys, x_eval, p):
    """Manual Lagrange interpolation at x_eval."""
    n = len(xs)
    result = 0
    for j in range(n):
        num = 1
        den = 1
        for s in range(n):
            if s == j: continue
            num = (num * (x_eval - xs[s])) % p
            den = (den * (xs[j] - xs[s])) % p
        den_inv = pow(den, p - 2, p)
        result = (result + ys[j] * num * den_inv) % p
    return result


def main():
    p = 1153
    n0, k0 = 64, 16
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2

    # Construct f
    pos = (35, 36, 39)
    coeffs = (1, 1, 1)
    fhat = [0] * n0
    for ps, c in zip(pos, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    # α=0 fold = f_e
    fold = f_e_arr.copy()

    # Pick T_info = (1, 3, 5, 7, 9, 11, 13, 15) ⊂ T (odd indices).
    T_info = [1, 3, 5, 7, 9, 11, 13, 15]
    print(f"T_info = {T_info}")
    print(f"L_1[T_info] = {[L1[i] for i in T_info]}")
    print(f"f_e[T_info] = {[f_e[i] for i in T_info]}")
    print()

    # Manual interpolation at all positions of L_1
    xs = [L1[i] for i in T_info]
    ys = [f_e[i] for i in T_info]
    interp = [lagrange_eval(xs, ys, L1[i], p) for i in range(n1)]
    print(f"Manual interp at L_1[i]: {interp}")
    print(f"f_e:                       {f_e}")

    matches = [interp[i] == f_e[i] for i in range(n1)]
    print(f"Matches: {matches}")
    print(f"# matches total: {sum(matches)}")
    extras_manual = sum(1 for i in range(n1) if matches[i] and i not in T_info)
    print(f"extras_manual (excluding T_info): {extras_manual}")

    # Now run batched_extras with this single T_info
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    T_batch = np.array([T_info], dtype=np.int64)
    extras_batched = batched_extras(T_batch, fold, L1_arr, D1, inv_D1, p)
    print(f"\nbatched_extras output: {int(extras_batched[0])}")

    if int(extras_batched[0]) != extras_manual:
        print(f"\n*** DISAGREEMENT BETWEEN MANUAL AND BATCHED ***")
    else:
        print(f"\n✓ Manual and batched agree.")


if __name__ == "__main__":
    main()
