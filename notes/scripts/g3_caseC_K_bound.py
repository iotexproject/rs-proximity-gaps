"""g3_caseC_K_bound.py — empirically test K bound for Case-C 3-pos sparse.

Case-C: supports with all-different mod-4 (1 empty quadrant). All 4
components a, b, c, d of fold² are nonzero — Note 0183's case analysis
does NOT cover this.

Key question: for Case-C under recursive above-J, what's max K? Is it
still ≤ 10 (universal), or does it differ?
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations, product
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
    info_sets = list(combinations(range(n1), k1))
    min_dist = n1
    for T in info_sets:
        x_vals = [int(L1_arr[i]) for i in T]
        y_vals = [int(fold1_arr[i]) for i in T]
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
    w_J_L1 = 8
    w_J_L2 = 4

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lp = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    print(f"=== Case-C K bound: 3-pos sparse, all-different mod-4 ===\n")

    # Enumerate Case-C supports: 1 j ∈ each of 3 different mod-4 quadrants
    case_c_supports = []
    j_by_q = [[], [], [], []]
    for j in range(k0, n0):
        j_by_q[j % 4].append(j)
    # Choose 3 of 4 quadrants, then 1 j from each
    for empty_q in range(4):
        active_qs = [q for q in range(4) if q != empty_q]
        for j1 in j_by_q[active_qs[0]]:
            for j2 in j_by_q[active_qs[1]]:
                for j3 in j_by_q[active_qs[2]]:
                    if j1 < j2 < j3:
                        case_c_supports.append((j1, j2, j3))

    print(f"Total Case-C supports (j's ≥ k_0=8): {len(case_c_supports)}")

    # Sample 50 random Case-C supports, run with random coefs
    random.seed(2026)
    sampled = random.sample(case_c_supports, min(50, len(case_c_supports)))

    case_c_results = []
    aboveJ_count = 0
    max_K = 0
    max_K_config = None

    for sup in sampled:
        # Find a coef set making f above-J at L_0 (just check one set)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        # Recursive above-J check at L_1
        d_max_L1 = 0
        for a1_test in [1, 2, 3, 5, 7, 11, 13]:
            fold1_arr = (fe_arr + a1_test * fo_arr) % p
            d_L1 = compute_dist_at_L1(fold1_arr, n1, k1, p, L1_arr)
            if d_L1 > d_max_L1: d_max_L1 = d_L1
        if d_max_L1 <= w_J_L1:
            continue
        aboveJ_count += 1

        # Compute K via bilinear sweep
        bad = np.zeros((p, p), dtype=np.int8)
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1_list = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1_list, L1, p)
            bad[a1, :] = per_alpha2_count(fold1_e, fold1_o, lp, p, n2, k2, w_J_L2)
        row = bad.sum(axis=1); col = bad.sum(axis=0)
        B1 = int((row == p).sum())
        K_col = int((col == p).sum())
        K = B1 + K_col

        case_c_results.append((sup, coefs, K, B1, K_col, d_max_L1))
        if K > max_K:
            max_K = K; max_K_config = (sup, coefs, K, B1, K_col)

    print(f"\nCase-C above-J count: {aboveJ_count} / {len(sampled)}")
    print(f"Case-C max K: {max_K}")
    if max_K_config:
        print(f"Max K config: sup={max_K_config[0]}, coefs={max_K_config[1]}, "
              f"K={max_K_config[2]}, B1={max_K_config[3]}, K_col={max_K_config[4]}")

    print(f"\nAll Case-C results (K ≥ 5):")
    for sup, coefs, K, B1, K_col, d_max in case_c_results:
        if K >= 5:
            print(f"  sup={sup}, K={K}, B1={B1}, K_col={K_col}, d_max_L1={d_max}")

    print(f"\nDistribution of K values across {aboveJ_count} above-J configs:")
    K_dist = {}
    for _, _, K, _, _, _ in case_c_results:
        K_dist[K] = K_dist.get(K, 0) + 1
    for K_val in sorted(K_dist):
        print(f"  K={K_val}: {K_dist[K_val]} configs")


if __name__ == "__main__":
    main()
