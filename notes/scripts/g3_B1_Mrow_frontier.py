"""g3_B1_Mrow_frontier.py — for ALL above-J 3-pos sparse supports at q=97,
compute (|B_1|, M_row, |V_δ|) and check the frontier:
   |V_δ| = |B_1|·q + (q − |B_1|)·M_row  ≤  (|B_1| + M_row)·q − |B_1|·M_row

The conjecture is that on the frontier:
   |B_1| + M_row ≤ 10   AND   |B_1| · M_row ≤ 9
giving |V_δ| ≤ 10q − 9.
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts, modinv
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def precompute_lagrange_pairs(L2_arr, info_sets_n2, p):
    n2 = len(L2_arr); pairs = []
    for T_idx, T in enumerate(info_sets_n2):
        i, j = int(T[0]), int(T[1])
        yi, yj = int(L2_arr[i]), int(L2_arr[j])
        denom_i = (yi - yj) % p; denom_j = (yj - yi) % p
        inv_di = modinv(denom_i, p); inv_dj = modinv(denom_j, p)
        T_set = {i, j}; kpairs = []
        for k in range(n2):
            if k in T_set: continue
            yk = int(L2_arr[k])
            c_ik = ((yk - yj) * inv_di) % p
            c_jk = ((yk - yi) * inv_dj) % p
            kpairs.append((k, c_ik, c_jk))
        pairs.append((T_idx, (i, j), kpairs))
    return pairs


def per_alpha2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]; fo = [int(x) for x in fold1_o]
    for T_idx, (i, j), kpairs in lagrange_pairs:
        always_count = 0; targets = []
        for k, c_ik, c_jk in kpairs:
            de = (c_ik * fe[i] + c_jk * fe[j] - fe[k]) % p
            do = (c_ik * fo[i] + c_jk * fo[j] - fo[k]) % p
            if do == 0:
                if de == 0: always_count += 1
            else:
                inv_do = modinv(do, p)
                alpha2 = (-de * inv_do) % p
                targets.append(alpha2)
        if always_count > 0: extras_per_T[T_idx, :] += always_count
        if targets:
            bc = np.bincount(np.array(targets, dtype=np.int64), minlength=p)
            extras_per_T[T_idx, :] += bc.astype(np.int32)
    max_extras = extras_per_T.max(axis=0)
    d2_vec = (n2 - k2 - max_extras).astype(np.int64)
    return (d2_vec <= w_J_L2).astype(np.int32)


def main():
    p = 97
    n0, k0, R = 32, 8, 2
    n2, k2 = 8, 2
    w_J_L0, w_J_L2 = 16, 4

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    rng_l0 = np.random.default_rng(2026)
    all_T_n0 = list(combinations(range(n0), k0))
    idx = rng_l0.choice(len(all_T_n0), size=30000, replace=False)
    info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)

    # FULL sweep over all 3-pos supports + 3 coef seeds each
    all_supports = list(combinations(range(8, 32), 3))
    n_seeds = 3
    sample = [(s, seed) for s in all_supports for seed in range(n_seeds)]
    print(f"Full sweep: {len(all_supports)} supports × {n_seeds} seeds = {len(sample)} configurations at q={p}")

    frontier_dist = Counter()  # (|B_1|, M_row, |V_δ|/q rounded)
    K_dist = Counter()  # K = |B_1| + K_col
    max_VD = 0
    max_examples = []
    max_K = 0
    max_K_examples = []
    import time as _time
    t0 = _time.time()
    for sup_idx, (sup, seed) in enumerate(sample):
        sup_rng = random.Random((42 + seed) ^ (hash(sup) & 0xFFFFFFFF))
        coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)
        ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
        d_f = n0 - k0 - int(ext.max())
        if d_f <= w_J_L0:
            continue  # below-J

        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64); fo_arr = np.array(f_o, dtype=np.int64)

        bad = np.zeros((p, p), dtype=np.int32)
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            bad[a1, :] = per_alpha2_count(fold1_e, fold1_o, lagrange_pairs,
                                            p, n2, k2, w_J_L2)
        VD = int(bad.sum())
        row = bad.sum(axis=1)  # row[α_1] = #{α_2 bad at α_1}
        col = bad.sum(axis=0)  # col[α_2] = #{α_1 bad at α_2}
        B1 = int((row == p).sum())
        K_col = int((col == p).sum())
        # M_row = max #{α_2 bad} over α_1's NOT in B_1
        non_sat_rows = row[row < p]
        M_row = int(non_sat_rows.max()) if len(non_sat_rows) > 0 else 0
        non_sat_cols = col[col < p]
        M_col = int(non_sat_cols.max()) if len(non_sat_cols) > 0 else 0

        # Predicted bound: |V_δ| = B_1·q + (q-B_1)·M_row
        predicted = B1 * p + (p - B1) * M_row
        ok = (VD == predicted) and (VD <= 10*p - 9)
        frontier_dist[(B1, M_row)] += 1
        K = B1 + K_col
        K_dist[K] += 1
        if K > max_K:
            max_K = K
            max_K_examples = [(sup, B1, K_col, M_row, M_col, VD)]
        elif K == max_K and len(max_K_examples) < 5:
            max_K_examples.append((sup, B1, K_col, M_row, M_col, VD))
        if VD > max_VD:
            max_VD = VD
            max_examples = [(sup, B1, K_col, M_row, M_col, VD)]
        elif VD == max_VD and len(max_examples) < 5:
            max_examples.append((sup, B1, K_col, M_row, M_col, VD))

        if (sup_idx+1) % 1000 == 0:
            print(f"  [{sup_idx+1}/{len(sample)}] max K so far: {max_K}, max |V_δ|: {max_VD} ({max_VD/p:.2f}q), elapsed: {_time.time()-t0:.0f}s")

    print(f"\n{'(|B_1|, M_row)':<16} count")
    print('-'*30)
    for k, n in sorted(frontier_dist.items()):
        print(f"  {str(k):<14} {n}")

    print(f"\nMax |V_δ|: {max_VD} (= {max_VD/p:.2f}q)")
    print(f"Top examples:")
    for sup, B1, K_col, M_row, M_col, VD in max_examples:
        print(f"  sup={sup} |B_1|={B1} K_col={K_col} M_row={M_row} M_col={M_col} |V_δ|={VD} ({VD/p:.2f}q)")

    print(f"\n=== Bluher orbit count K = |B_1| + K_col ===")
    print(f"K distribution:")
    for K, n in sorted(K_dist.items()):
        print(f"  K={K:<3} count={n}")
    print(f"\nMax K = {max_K}; conjecture K ≤ 10 = n_1 - s + 2: {'HOLDS' if max_K <= 10 else 'VIOLATED'}")
    print(f"Top K examples:")
    for sup, B1, K_col, M_row, M_col, VD in max_K_examples:
        print(f"  sup={sup} |B_1|+K_col = {B1+K_col} = {B1}+{K_col}, M_row={M_row}, |V_δ|={VD}")

    print(f"\n=== Frontier check ===")
    print(f"{'(|B_1|, M_row)':<16} {'pred|V_δ|':<10} {'A·B':<5} {'A+B':<5} {'≤ 10q-9?'}")
    print('-'*60)
    for (B1, M_row), n in sorted(frontier_dist.items()):
        pred = B1 * p + (p - B1) * M_row
        prod = B1 * M_row
        sm = B1 + M_row
        ok = (pred <= 10 * p - 9)
        print(f"  {str((B1, M_row)):<14} {pred:<10} {prod:<5} {sm:<5} {ok}")


if __name__ == "__main__":
    main()
