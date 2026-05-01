"""g3_64_16_h_pencil_aboveJ.py — verify h(α_1) pencil at L_2 is above-J at L_2
for (64, 16) Reverse Pattern saturating examples.

This is the key hypothesis of Note 0183.b extension. If yes, K ≤ M_max(L_2) + 1 = 10.

Saturating example: (43, 50, 51) Reverse. We compute:
  h(α_1) := c + α_1·d on L_2 of order 16, where c=(f_e)_o, d=(f_o)_o.
And test whether max_α_1 dist(h(α_1), RS_4(L_2)) > w_J(L_2) = 8.
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain, even_odd_parts, modinv


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def dist_to_RS_at_L2(arr, n2, k2, p, L2_arr, info_sets_sample=None):
    """Compute (or sample) dist(arr, RS_{k_2}(L_2)).

    For each info_set T of size k_2, fit polynomial of degree < k_2 through
    those points, count agreements; dist = n_2 - max(agreements).
    """
    if info_sets_sample is None:
        info_sets_sample = list(combinations(range(n2), k2))
    min_dist = n2
    arr_list = [int(x) for x in arr]
    L_list = [int(x) for x in L2_arr]
    for T in info_sets_sample:
        x_vals = [L_list[i] for i in T]
        y_vals = [arr_list[i] for i in T]
        agree = 0
        for j in range(n2):
            xj = L_list[j]
            val = 0
            for i_idx, i in enumerate(T):
                xi = x_vals[i_idx]
                num = 1; den = 1
                for jj_idx in range(len(T)):
                    if jj_idx == i_idx: continue
                    xjj = x_vals[jj_idx]
                    num = (num * (xj - xjj)) % p
                    den = (den * (xi - xjj)) % p
                Li = (num * modinv(den, p)) % p
                val = (val + y_vals[i_idx] * Li) % p
            if val == arr_list[j]:
                agree += 1
        d = n2 - agree
        if d < min_dist: min_dist = d
    return min_dist


def main():
    p = 193
    n0, k0 = 64, 16
    n1, k1 = 32, 8
    n2, k2 = 16, 4
    w_J_L2 = 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)

    print(f"=== (64, 16) h pencil above-J at L_2 — Note 0183.b verification ===\n")
    print(f"  q={p}, L_2 order {n2}, k_2={k2}, w_J(L_2)={w_J_L2}, M_max(L_2)=9\n")

    # Test cases: known saturating Reverse and Pattern B at (64, 16)
    test_cases = [
        ((43, 50, 51), "Reverse"),         # documented saturating
        ((33, 39, 51), "Reverse"),
        ((33, 35, 39), "Pattern B all-odd"),
        ((35, 39, 47), "Pattern B all-odd"),
    ]

    info_sets_n2 = list(combinations(range(n2), k2))
    print(f"  Total info_sets at L_2: {len(info_sets_n2)} (full enumeration)\n")

    for sup, label in test_cases:
        print(f"--- sup={sup} ({label}) ---")
        for trial in range(3):
            random.seed(2026 + trial + sum(sup))
            coefs = [random.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p
            f = evaluate_dft(fhat, L0, p)
            f_e, f_o = even_odd_parts(f, L0, p)

            # Get c = (f_e)_o and d = (f_o)_o on L_2 (Reverse pencil)
            fe_e, fe_o = even_odd_parts(f_e, L1, p)  # (f_e)_e, (f_e)_o on L_2
            fo_e, fo_o = even_odd_parts(f_o, L1, p)  # (f_o)_e, (f_o)_o on L_2

            # For Reverse: h(α_1) = (f_e)_o + α_1·(f_o)_o on L_2
            # For Pattern B: g(α_2) = (f_o)_e + α_2·(f_o)_o on L_2

            mod4 = tuple(j % 4 for j in sup)
            # Determine pattern empirically
            a_zero = all(int(x) == 0 for x in fe_e)
            b_zero = all(int(x) == 0 for x in fo_e)
            c_zero = all(int(x) == 0 for x in fe_o)
            d_zero = all(int(x) == 0 for x in fo_o)
            print(f"  Trial {trial}, coefs={coefs}, mod4={mod4}")
            print(f"    a={'0' if a_zero else '≠0'}, b={'0' if b_zero else '≠0'}, "
                  f"c={'0' if c_zero else '≠0'}, d={'0' if d_zero else '≠0'}")

            if a_zero and b_zero and not c_zero and not d_zero:
                # Reverse: h pencil = c + α_1·d
                pencil_c = fe_o; pencil_d = fo_o
                pencil_label = "h(α_1) = c + α_1·d (Reverse)"
            elif a_zero and c_zero and not b_zero and not d_zero:
                # Pattern B: g pencil = b + α_2·d
                pencil_c = fo_e; pencil_d = fo_o
                pencil_label = "g(α_2) = b + α_2·d (Pattern B)"
            else:
                print(f"    Not B nor Reverse — skipping pencil test.")
                continue

            print(f"    Pencil: {pencil_label}")

            # Sample multiple α values and measure dist
            d_max = 0
            for alpha in [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
                pencil_val = [(int(pencil_c[i]) + alpha * int(pencil_d[i])) % p
                             for i in range(n2)]
                d = dist_to_RS_at_L2(pencil_val, n2, k2, p, L2_arr, info_sets_n2)
                if d > d_max: d_max = d

            above_J = d_max > w_J_L2
            print(f"    max dist(pencil(α), RS_4(L_2)) over α tested = {d_max}")
            print(f"    above-J at L_2? {'YES' if above_J else 'NO'} (need d > {w_J_L2})")
        print()


if __name__ == "__main__":
    main()
