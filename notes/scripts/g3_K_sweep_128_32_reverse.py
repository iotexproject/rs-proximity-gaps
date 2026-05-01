"""g3_K_sweep_128_32_reverse.py — sweep Reverse-pattern supports at (128,32)
to characterize saturating support patterns.

For each support with mod-4 ⊂ {2, 3} (Reverse Pattern):
  - Filter for recursive above-J at L_1
  - Compute K = |B_1| + K_col

Goal: find structural rule for K = 10 saturation.
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
    p = 257
    n0, k0, R = 128, 32, 2
    n1, k1 = 64, 16
    n2, k2 = 32, 8
    w_J_L0, w_J_L1, w_J_L2 = 64, 32, 16

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    rng = np.random.default_rng(2026)
    info_sample_n2 = []; seen = set()
    while len(info_sample_n2) < 5000:
        T = tuple(sorted(rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n2.append(T)
    info_sets_n2 = np.array(info_sample_n2, dtype=np.int64)

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

    print("Precomputing Lagrange pairs at L_2...")
    t_lag = time.time()
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)
    print(f"  Done in {time.time() - t_lag:.0f}s")

    # Generate Reverse Pattern supports: mod-4 ⊂ {2, 3}, all positions ≥ k_0 = 32
    reverse_positions = [j for j in range(k0, n0) if j % 4 in (2, 3)]
    print(f"\nReverse-eligible positions ≥ {k0}: {len(reverse_positions)}")

    all_reverse = list(combinations(reverse_positions, 3))
    print(f"Total Reverse 3-pos supports: {len(all_reverse)}")

    rng_s = random.Random(2026)
    sample_supports = rng_s.sample(all_reverse, 60)

    K_dist = Counter()
    saturating = []
    high_K_examples = []  # K ≥ 5
    n_aboveJ = 0
    n_total = 0
    t0 = time.time()

    print(f"\n=== Sweeping {len(sample_supports)} Reverse-pattern supports at (128, 32) ===")

    for idx, sup in enumerate(sample_supports):
        n_total += 1
        random.seed(2026 + hash(sup) % 1000)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)
        ext_n0 = batched_extras(info_sets_n0_sample, f_arr, L0_arr, D0, inv_D0, p)
        d_f = n0 - k0 - int(ext_n0.max())
        if d_f <= w_J_L0:
            K_dist[-1] += 1  # not above-J
            continue

        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        d_fold_max = 0
        for a1_test in [1, 2, 3, 5, 7, 11, 13]:
            fold1_test = (fe_arr + a1_test * fo_arr) % p
            ext_t = batched_extras(info_sets_n1_sample, fold1_test, L1_arr, D1, inv_D1, p)
            d_t = n1 - k1 - int(ext_t.max())
            if d_t > d_fold_max: d_fold_max = d_t
        if d_fold_max <= w_J_L1:
            K_dist[-1] += 1
            continue
        n_aboveJ += 1

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

        K_dist[K] += 1
        if K == 10:
            saturating.append((sup, B1, K_col, VD))
        if K >= 5:
            high_K_examples.append((sup, K, B1, K_col, VD))

        if (idx + 1) % 10 == 0:
            elapsed = time.time() - t0
            print(f"  [{idx+1}/{len(sample_supports)}: aboveJ={n_aboveJ}, "
                  f"sat(K=10)={len(saturating)}, K_dist={dict(K_dist)}, "
                  f"elapsed={elapsed:.0f}s]")

    elapsed = time.time() - t0
    print(f"\nFinal: total={n_total}, aboveJ={n_aboveJ}, sat(K=10)={len(saturating)}")
    print(f"K dist: {dict(K_dist)}")
    print(f"Elapsed: {elapsed:.0f}s")

    if saturating:
        print(f"\n=== {len(saturating)} K=10 saturating supports ===")
        for sup, B1, K_col, VD in saturating[:15]:
            mod4 = tuple(j % 4 for j in sup)
            print(f"  {sup}, mod4={mod4}, B1={B1}, K_col={K_col}, |V_δ|={VD}")

    if high_K_examples:
        print(f"\n=== High-K examples (K ≥ 5) — {len(high_K_examples)} configs ===")
        for sup, K, B1, K_col, VD in high_K_examples[:15]:
            mod4 = tuple(j % 4 for j in sup)
            print(f"  {sup}, mod4={mod4}, K={K}, B1={B1}, K_col={K_col}, |V_δ|={VD}")


if __name__ == "__main__":
    main()
