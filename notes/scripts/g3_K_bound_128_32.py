"""g3_K_bound_128_32.py — test K bound at (128, 32) larger scale.

Target: 1-3 Reverse/Pattern-B specific supports at (128, 32), q=257.
Compute K = |B_1| + K_col via bilinear sweep with SAMPLED info_sets at L_2.

If K ≤ 10: K is truly scale-universal (10 = M_max at order-16 level extends).
If K → 18 (= M_max(L_2) at order 32 = 17 + 1): K = O(n_0/8) growth.
"""
import sys, os, random, time
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
    p = 257  # smallest q ≡ 1 mod 128 (need 128 | q-1)
    n0, k0, R = 128, 32, 2
    n1, k1 = 64, 16
    n2, k2 = 32, 8
    w_J_L0, w_J_L1, w_J_L2 = 64, 32, 16

    print(f"=== K bound at (128, 32), q={p} ===")
    print(f"  L_0 order {n0}, L_1 order {n1}, L_2 order {n2}")
    print(f"  w_J(L_0)={w_J_L0}, w_J(L_1)={w_J_L1}, w_J(L_2)={w_J_L2}")
    print(f"  M_max(L_1)={n1 - 16 + 1}=49, M_max(L_2)={n2 - 16 + 1}=17")
    print(f"  Test: K ≤ 10 (universal) vs K ≤ 18 (1+M_max(L_2)) vs K ≤ 50 (1+M_max(L_1))\n")

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    # Sample info_sets_n2 — too many to enumerate (C(32,8) = 10.5M)
    rng = np.random.default_rng(2026)
    info_sample_n2 = []; seen = set()
    while len(info_sample_n2) < 5000:  # 5K — keep precomputation small
        T = tuple(sorted(rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n2.append(T)
    info_sets_n2 = np.array(info_sample_n2, dtype=np.int64)
    print(f"  Sampled info_sets at L_2: {len(info_sets_n2)} (out of {2598960:,})\n")

    print("Precomputing Lagrange pairs at L_2...")
    t_lag = time.time()
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)
    print(f"  Done in {time.time() - t_lag:.0f}s\n")

    # Sample info_sets_n0 and info_sets_n1
    info_sample_n0 = []; seen = set()
    while len(info_sample_n0) < 30000:
        T = tuple(sorted(rng.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n0.append(T)
    info_sets_n0_sample = np.array(info_sample_n0, dtype=np.int64)

    info_sample_n1 = []; seen = set()
    while len(info_sample_n1) < 5000:
        T = tuple(sorted(rng.choice(n1, size=k1, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n1.append(T)
    info_sets_n1_sample = np.array(info_sample_n1, dtype=np.int64)

    # Test supports — 3 Reverse-pattern at (128, 32)
    test_supports = [
        (35, 38, 39),   # mod-4 = (3, 2, 3) Reverse
        (87, 102, 103), # mod-4 = (3, 2, 3) Reverse, larger positions
        (43, 50, 51),   # mod-4 = (3, 2, 3) Reverse, deployment-style
    ]

    for sup in test_supports:
        print(f"\n--- sup={sup}, mod-4={tuple(j % 4 for j in sup)} ---")
        random.seed(2026 + hash(sup) % 1000)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)

        # Check d_f at L_0 (recursive above-J condition #1)
        ext_n0 = batched_extras(info_sets_n0_sample, f_arr, L0_arr, D0, inv_D0, p)
        d_f = n0 - k0 - int(ext_n0.max())
        print(f"  coefs={coefs}, d_f at L_0 = {d_f} (need > {w_J_L0})")
        if d_f <= w_J_L0:
            print(f"  SKIP: not above-J at L_0")
            continue

        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        # Probe d(fold¹(α_1)) for several α_1
        d_fold_max = 0
        for a1_test in [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]:
            fold1_test = (fe_arr + a1_test * fo_arr) % p
            ext_t = batched_extras(info_sets_n1_sample, fold1_test, L1_arr, D1, inv_D1, p)
            d_t = n1 - k1 - int(ext_t.max())
            if d_t > d_fold_max: d_fold_max = d_t
        print(f"  max d(fold¹(α_1)) at L_1 = {d_fold_max} (need > {w_J_L1})")
        if d_fold_max <= w_J_L1:
            print(f"  SKIP: not above-J at L_1 (recursive)")
            continue

        # Bilinear K sweep
        print(f"  Running bilinear sweep ({p}² = {p*p:,} iterations)...")
        t0 = time.time()
        bad = np.zeros((p, p), dtype=np.int32)
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            bad[a1, :] = per_alpha2_count(fold1_e, fold1_o, lagrange_pairs,
                                            p, n2, k2, w_J_L2)
            if (a1 + 1) % 50 == 0:
                elapsed = time.time() - t0
                est_total = elapsed * p / (a1 + 1)
                print(f"    [α_1={a1+1}/{p}, elapsed={elapsed:.0f}s, est_total={est_total:.0f}s]")
        elapsed = time.time() - t0

        VD = int(bad.sum())
        row = bad.sum(axis=1); col = bad.sum(axis=0)
        B1 = int((row == p).sum())
        K_col = int((col == p).sum())
        K = B1 + K_col

        print(f"  K = {K} (B1={B1}, K_col={K_col}), |V_δ| = {VD}")
        print(f"  K ≤ 10? {'YES' if K <= 10 else 'NO'}")
        print(f"  K ≤ 18? {'YES' if K <= 18 else 'NO'}")
        print(f"  Sweep time: {elapsed:.0f}s")


if __name__ == "__main__":
    main()
