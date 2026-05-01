"""g3_64_16_atJ_K_test.py — measure K for (64, 16) supports with pencil at-J at L_2.

Previous Note 0183.b verification (g3_64_16_h_pencil_aboveJ.py) showed that
(33, 35, 39) and (35, 39, 47) have pencil at-J at L_2 (max dist ≤ w_J).

Question: do these give K = 2q (like (67,90,91) at 128,32), or K bounded?

If K is bounded at (64,16) at-J cases, then (64,16) has tighter structure
than (128,32). If K = 2q, the at-J anomaly extends to (64,16) too.
"""
import sys, os, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
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
        idxs = [int(t) for t in T]
        T_set = set(idxs)
        kpairs = []
        for k in range(n2):
            if k in T_set: continue
            yk = int(L2_arr[k])
            coeffs = []
            for ii in idxs:
                yi = int(L2_arr[ii])
                num = 1; den = 1
                for jj in idxs:
                    if jj == ii: continue
                    yj = int(L2_arr[jj])
                    num = (num * (yk - yj)) % p
                    den = (den * (yi - yj)) % p
                coeffs.append((ii, (num * modinv(den, p)) % p))
            kpairs.append((k, coeffs))
        pairs.append((T_idx, idxs, kpairs))
    return pairs


def per_alpha2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]; fo = [int(x) for x in fold1_o]
    for T_idx, idxs, kpairs in lagrange_pairs:
        always_count = 0; targets = []
        for k, coeffs in kpairs:
            pred_e = 0; pred_o = 0
            for (ii, c_ii) in coeffs:
                pred_e = (pred_e + c_ii * fe[ii]) % p
                pred_o = (pred_o + c_ii * fo[ii]) % p
            de = (pred_e - fe[k]) % p
            do = (pred_o - fo[k]) % p
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
    p = 193
    n0, k0, R = 64, 16, 2
    n1, k1 = 32, 8
    n2, k2 = 16, 4
    w_J_L0, w_J_L1, w_J_L2 = 32, 16, 8

    print(f"=== (64, 16) at-J K test, q={p} ===\n")
    print(f"  Test: (33,35,39) and (35,39,47) had pencil at-J at L_2.")
    print(f"  Question: are K = 2q (= {2*p}) or bounded?\n")

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    # FULL info_sets at L_2 (C(16, 4) = 1820, manageable)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    print(f"info_sets at L_2: {len(info_sets_n2)} (full enumeration)")

    print("Precomputing Lagrange pairs at L_2...")
    t_lag = time.time()
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)
    print(f"  Done in {time.time() - t_lag:.0f}s")

    rng = np.random.default_rng(2026)
    info_sample_n0 = []; seen = set()
    while len(info_sample_n0) < 30000:
        T = tuple(sorted(rng.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n0.append(T)
    info_sets_n0_sample = np.array(info_sample_n0, dtype=np.int64)

    # Test the at-J supports with multiple coef trials
    test_supports = [
        (33, 35, 39),  # mod-4 = (1, 3, 3)
        (35, 39, 47),  # mod-4 = (3, 3, 3) — degenerate, b=c=0
        (33, 39, 51),  # mod-4 = (1, 3, 3) — was above-J (control)
        (43, 50, 51),  # mod-4 = (3, 2, 3) — known saturating (control)
    ]

    for sup in test_supports:
        print(f"\n--- sup={sup}, mod-4={tuple(j%4 for j in sup)} ---")
        for trial in range(3):
            random.seed(2026 + trial + sum(sup))
            coefs = [random.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p

            f = evaluate_dft(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            ext_n0 = batched_extras(info_sets_n0_sample, f_arr, L0_arr, D0, inv_D0, p)
            d_f = n0 - k0 - int(ext_n0.max())
            if d_f <= w_J_L0:
                print(f"  Trial {trial}: SKIP (not above-J at L_0)"); continue

            f_e, f_o = even_odd_parts(f, L0, p)
            fe_arr = np.array(f_e, dtype=np.int64)
            fo_arr = np.array(f_o, dtype=np.int64)
            fe_e, fe_o = even_odd_parts(f_e, L1, p)
            fo_e, fo_o = even_odd_parts(f_o, L1, p)

            # Determine pattern
            a_zero = all(int(x) == 0 for x in fe_e)
            b_zero = all(int(x) == 0 for x in fo_e)
            c_zero = all(int(x) == 0 for x in fe_o)
            d_zero = all(int(x) == 0 for x in fo_o)

            # Compute pencil dist at L_2
            if a_zero and b_zero:
                pc, pd = fe_o, fo_o; pencil_label = "h(α_1) Reverse"
            elif a_zero and c_zero:
                pc, pd = fo_e, fo_o; pencil_label = "g(α_2) PatB"
            else:
                pc, pd = fe_o, fo_o; pencil_label = "h(α_1) gen"
            pc_arr = np.array(pc, dtype=np.int64)
            pd_arr = np.array(pd, dtype=np.int64)
            d_pencil_max = 0
            for alpha in [0, 1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
                pv = (pc_arr + alpha * pd_arr) % p
                ext = batched_extras(info_sets_n2, pv, L2_arr, D2, inv_D2, p)
                d_t = n2 - k2 - int(ext.max())
                if d_t > d_pencil_max: d_pencil_max = d_t
            above_J_L2 = d_pencil_max > w_J_L2

            # Compute K via bilinear sweep
            bad = np.zeros((p, p), dtype=np.int32)
            for a1 in range(p):
                fold1_arr = (fe_arr + a1 * fo_arr) % p
                fold1 = fold1_arr.tolist()
                fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
                bad[a1, :] = per_alpha2_count(fold1_e, fold1_o, lagrange_pairs,
                                                p, n2, k2, w_J_L2)
            row = bad.sum(axis=1); col = bad.sum(axis=0)
            B1 = int((row == p).sum())
            K_col = int((col == p).sum())
            K = B1 + K_col

            print(f"  Trial {trial}: coefs={coefs}, pencil={pencil_label}, "
                  f"pencil_d_max={d_pencil_max} ({'above' if above_J_L2 else 'AT/below'}-J), "
                  f"K={K} (B1={B1}, K_col={K_col})")


if __name__ == "__main__":
    main()
