"""g3_reverse_15_18_19_verify.py — verify Reverse Pattern (15, 18, 19) at (32, 8).

Per Note 0178: |V_δ| = 10q-9 with (|B_1|, K_col) = (9, 1).
Per Note 0182: this is the "1-monomial sign-character bypass" case.
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
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L2 = 4

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    sup = (15, 18, 19)
    print(f"=== Reverse Pattern verification: sup={sup} at (32, 8), q={p} ===")
    print(f"  mod-4 = {tuple(j%4 for j in sup)}")
    print(f"  L_2 = {L2[:4]}... (n_2 = {n2})")

    for trial in range(3):
        random.seed(2026 + trial)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        # Further split
        fe_e, fe_o = even_odd_parts(f_e, L1, p)  # f_e on L_1 → (f_e)_e + (f_e)_o on L_2
        fo_e, fo_o = even_odd_parts(f_o, L1, p)  # f_o on L_1 → (f_o)_e + (f_o)_o on L_2

        print(f"\nTrial {trial}, coefs={coefs}:")
        print(f"  (f_e)_e on L_2: {[int(x) for x in fe_e]} ({'≡ 0' if all(x==0 for x in fe_e) else 'nonzero'})")
        print(f"  (f_o)_e on L_2: {[int(x) for x in fo_e]} ({'≡ 0' if all(x==0 for x in fo_e) else 'nonzero'})")
        print(f"  (f_e)_o on L_2: {[int(x) for x in fe_o]} ({'≡ 0' if all(x==0 for x in fe_o) else 'nonzero'})")
        print(f"  (f_o)_o on L_2: {[int(x) for x in fo_o]} ({'≡ 0' if all(x==0 for x in fo_o) else 'nonzero'})")

        # Compute |B_1|, K_col
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)
        bad = np.zeros((p, p), dtype=np.int32)
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            bad[a1, :] = per_alpha2_count(fold1_e, fold1_o, lagrange_pairs,
                                            p, n2, k2, w_J_L2)
        VD = int(bad.sum())
        row = bad.sum(axis=1); col = bad.sum(axis=0)
        B1 = int((row == p).sum())
        K_col = int((col == p).sum())
        K = B1 + K_col

        # Identify the saturating α_1's
        sat_rows = np.where(row == p)[0].tolist()
        sat_cols = np.where(col == p)[0].tolist()

        print(f"  K = {K} (B_1 = {B1}, K_col = {K_col}), |V_δ| = {VD}")
        print(f"  Saturating α_1's: {sat_rows[:15]}{'...' if len(sat_rows) > 15 else ''}")
        print(f"  Saturating α_2's: {sat_cols}")


if __name__ == "__main__":
    main()
