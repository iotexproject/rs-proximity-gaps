"""g3_verify_B1_subset_L1bad.py — empirical sanity check for Note 0183 proof.

Claim: For any 3-pos sparse f̂ at (32, 8) under recursive above-J,
       B_1 ⊂ {α_1 : fold¹(α_1) bad at L_1}.

Method: For multiple supports + coef trials:
  1. Compute B_1 directly via the bilinear sweep.
  2. Compute "L_1-bad set" = {α_1 : dist(fold¹(α_1), RS_4(L_1)) ≤ 8}.
  3. Verify B_1 ⊂ L_1-bad.

Also verify |L_1-bad| ≤ 9 = M_max(L_1) under recursive above-J.
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


def precompute_lagrange_pairs(L_arr, info_sets, p):
    n = len(L_arr); pairs = []
    for T_idx, T in enumerate(info_sets):
        i, j = int(T[0]), int(T[1])
        yi, yj = int(L_arr[i]), int(L_arr[j])
        denom_i = (yi - yj) % p; denom_j = (yj - yi) % p
        inv_di = modinv(denom_i, p); inv_dj = modinv(denom_j, p)
        T_set = {i, j}; kpairs = []
        for k in range(n):
            if k in T_set: continue
            yk = int(L_arr[k])
            c_ik = ((yk - yj) * inv_di) % p
            c_jk = ((yk - yi) * inv_dj) % p
            kpairs.append((k, c_ik, c_jk))
        pairs.append((T_idx, (i, j), kpairs))
    return pairs


def per_alpha2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J):
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]; fo = [int(x) for x in fold1_o]
    for T_idx, (i, j), kpairs in lagrange_pairs:
        always = 0; targets = []
        for k, c_ik, c_jk in kpairs:
            de = (c_ik * fe[i] + c_jk * fe[j] - fe[k]) % p
            do = (c_ik * fo[i] + c_jk * fo[j] - fo[k]) % p
            if do == 0:
                if de == 0: always += 1
            else:
                a2 = (-de * modinv(do, p)) % p
                targets.append(a2)
        if always: extras_per_T[T_idx, :] += always
        if targets:
            bc = np.bincount(np.array(targets, dtype=np.int64), minlength=p)
            extras_per_T[T_idx, :] += bc.astype(np.int32)
    max_ex = extras_per_T.max(axis=0)
    d_vec = (n2 - k2 - max_ex)
    return (d_vec <= w_J).astype(np.int8)


def compute_dist_at_L1(fold1_arr, n1, k1, p, L1_arr):
    """Compute exact dist(fold1, RS_4(L_1)) by enumerating info_sets at L_1."""
    info_sets = list(combinations(range(n1), k1))
    min_dist = n1
    for T in info_sets:
        # Lagrange interpolation through k_1=4 points
        x_vals = [int(L1_arr[i]) for i in T]
        y_vals = [int(fold1_arr[i]) for i in T]
        # Fit degree < 4 poly through 4 points (unique)
        # Then count agreements
        # Use Lagrange basis
        agree = 0
        for j in range(n1):
            xj = int(L1_arr[j])
            val = 0
            for i_idx, i in enumerate(T):
                xi = x_vals[i_idx]
                num = 1; den = 1
                for jj_idx, jj in enumerate(T):
                    if jj_idx == i_idx: continue
                    xjj = x_vals[jj_idx]
                    num = (num * (xj - xjj)) % p
                    den = (den * (xi - xjj)) % p
                Li = (num * modinv(den, p)) % p
                val = (val + y_vals[i_idx] * Li) % p
            if val == int(fold1_arr[j]):
                agree += 1
        d = n1 - agree
        if d < min_dist: min_dist = d
    return min_dist


def main():
    p = 97
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L1 = n1 - 8  # = 8
    w_J_L2 = 4

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lp = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    print(f"=== Verify B_1 ⊂ L_1-bad set (proof of Note 0183) ===\n")
    print(f"  L_0 order {n0}, L_1 order {n1}, L_2 order {n2}")
    print(f"  w_J(L_1) = {w_J_L1}, w_J(L_2) = {w_J_L2}")
    print(f"  M_max(L_1) = {n1 - 8 + 1} = 9")
    print()

    # Test on multiple support patterns
    test_supports = [
        (15, 18, 19),   # Reverse Pattern
        (1, 3, 5),      # Pattern B (all-odd)
        (3, 5, 18),     # Reverse Pattern
        (15, 19, 22),   # Reverse Pattern
        (1, 3, 7),      # Pattern B
        (5, 7, 9),      # Pattern B
    ]

    for sup in test_supports:
        for trial in range(2):
            random.seed(2026 + trial + hash(sup) % 1000)
            coefs = [random.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p
            f = evaluate_dft(fhat, L0, p)
            f_e, f_o = even_odd_parts(f, L0, p)

            # Compute |B_1| set + check via L_1-bad set
            fe_arr = np.array(f_e, dtype=np.int64)
            fo_arr = np.array(f_o, dtype=np.int64)

            # First check recursive above-J: ∃α_1 with fold¹(α_1) above-J at L_1
            d_max_L1 = 0
            for a1_test in range(p):
                fold1_arr = (fe_arr + a1_test * fo_arr) % p
                d_L1 = compute_dist_at_L1(fold1_arr, n1, k1, p, L1_arr)
                if d_L1 > d_max_L1: d_max_L1 = d_L1
            recursive_aboveJ = d_max_L1 > w_J_L1

            # Compute B_1 set via bilinear sweep
            B_1_set = []
            for a1 in range(p):
                fold1_arr = (fe_arr + a1 * fo_arr) % p
                fold1_list = fold1_arr.tolist()
                fold1_e, fold1_o = even_odd_parts(fold1_list, L1, p)
                row_bad = per_alpha2_count(fold1_e, fold1_o, lp, p, n2, k2, w_J_L2)
                if int(row_bad.sum()) == p:
                    B_1_set.append(a1)

            # Compute L_1-bad set: {α_1 : dist(fold¹(α_1), RS_4(L_1)) ≤ 8}
            L1_bad_set = []
            for a1 in range(p):
                fold1_arr = (fe_arr + a1 * fo_arr) % p
                d_L1 = compute_dist_at_L1(fold1_arr, n1, k1, p, L1_arr)
                if d_L1 <= w_J_L1:
                    L1_bad_set.append(a1)

            B_1_set = set(B_1_set); L1_bad_set = set(L1_bad_set)
            subset = B_1_set.issubset(L1_bad_set)

            print(f"sup={sup}, coefs={coefs}, max d at L_1 = {d_max_L1} ({'above-J' if recursive_aboveJ else 'NOT above-J'})")
            print(f"  |B_1| = {len(B_1_set)}: {sorted(B_1_set)}")
            print(f"  |L_1-bad| = {len(L1_bad_set)}: {sorted(L1_bad_set)[:15]}{'...' if len(L1_bad_set) > 15 else ''}")
            print(f"  B_1 ⊂ L_1-bad? {subset}")
            print(f"  |L_1-bad| ≤ 9? {len(L1_bad_set) <= 9}")
            if not subset:
                print(f"  ⚠️ COUNTEREXAMPLE: extra in B_1: {sorted(B_1_set - L1_bad_set)}")
            print()


if __name__ == "__main__":
    main()
