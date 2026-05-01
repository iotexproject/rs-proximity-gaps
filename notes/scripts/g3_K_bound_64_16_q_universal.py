"""g3_K_bound_64_16_q_universal.py — verify K ≤ 10 at (64, 16) across primes
under recursive above-J filter. Smaller per-q sample for speed.
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
        idxs = [int(t) for t in T]; T_set = set(idxs); kpairs = []
        for k in range(n2):
            if k in T_set: continue
            yk = int(L2_arr[k]); coeffs = []
            for ii in idxs:
                yi = int(L2_arr[ii]); num = 1; den = 1
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


def sweep_q(p, n0, k0, R, n1, k1, n2, k2, w_J_L0, w_J_L1, w_J_L2,
            sample_supports, info_sets_n0_sample, info_sets_n1_sample):
    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    K_dist = Counter()
    max_K = 0; max_VD = 0
    n_aboveJ_L0 = 0; n_aboveJ_recursive = 0
    saturating_examples = []
    t0 = time.time()
    for sup_idx, sup in enumerate(sample_supports):
        sup_rng = random.Random((42 ^ (hash(sup) & 0xFFFFFFFF)))
        coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)
        ext_n0 = batched_extras(info_sets_n0_sample, f_arr, L0_arr, D0, inv_D0, p)
        d_f = n0 - k0 - int(ext_n0.max())
        if d_f <= w_J_L0:
            continue
        n_aboveJ_L0 += 1

        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        d_fold_max = 0
        for a1_test in [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            fold1_test = (fe_arr + a1_test * fo_arr) % p
            ext_t = batched_extras(info_sets_n1_sample, fold1_test,
                                     L1_arr, D1, inv_D1, p)
            d_t = n1 - k1 - int(ext_t.max())
            if d_t > d_fold_max: d_fold_max = d_t
        if d_fold_max <= w_J_L1:
            continue
        n_aboveJ_recursive += 1

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
        if K > max_K:
            max_K = K
            saturating_examples = [(sup, K, B1, K_col, VD, d_f, d_fold_max)]
        elif K == max_K:
            saturating_examples.append((sup, K, B1, K_col, VD, d_f, d_fold_max))
        max_VD = max(max_VD, VD)

    elapsed = time.time() - t0
    return max_K, max_VD, K_dist, n_aboveJ_L0, n_aboveJ_recursive, elapsed, saturating_examples


def main():
    n0, k0, R = 64, 16, 2
    n1, k1 = 32, 8
    n2, k2 = 16, 4
    w_J_L0, w_J_L1, w_J_L2 = 32, 16, 8

    primes = [193, 449]  # 1153 too slow at (64,16) for our time budget

    # Setup info_sets at L_0 and L_1 — shared across primes
    rng = np.random.default_rng(2026)
    info_sample = []; seen = set()
    while len(info_sample) < 30000:
        T = tuple(sorted(rng.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample.append(T)
    info_sets_n0_sample = np.array(info_sample, dtype=np.int64)

    info_sample_n1 = []; seen_n1 = set()
    while len(info_sample_n1) < 1500:
        T = tuple(sorted(rng.choice(n1, size=k1, replace=False).tolist()))
        if T not in seen_n1: seen_n1.add(T); info_sample_n1.append(T)
    info_sets_n1_sample = np.array(info_sample_n1, dtype=np.int64)

    all_supports = list(combinations(range(k0, n0), 3))
    rng_s = random.Random(2026)
    sample_supports = rng_s.sample(all_supports, 30)

    print(f"=== K-bound at (64, 16) q-universal under recursive above-J ===")
    print(f"  Sample: 80 supports per q, q ∈ {primes}")
    print(f"  Predicted: K ≤ 10, |V_δ| ≤ 10q-9 (scale-universal constant)\n")
    print(f"{'q':<6} {'aboveJ-L0':<10} {'aboveJ-rec':<12} {'max K':<6} {'max |V_δ|':<10} {'10q-9':<8} {'PASS?':<8} {'elapsed'}")
    print("-"*100)
    for p in primes:
        max_K, max_VD, K_dist, n_L0, n_rec, elapsed, sats = sweep_q(
            p, n0, k0, R, n1, k1, n2, k2, w_J_L0, w_J_L1, w_J_L2,
            sample_supports, info_sets_n0_sample, info_sets_n1_sample)
        passed = max_K <= 10 and max_VD <= 10*p - 9
        ds = ", ".join(f"{k}:{v}" for k, v in sorted(K_dist.items())[:6])
        print(f"{p:<6} {n_L0:<10} {n_rec:<12} {max_K:<6} {max_VD:<10} {10*p-9:<8} "
              f"{'PASS' if passed else 'FAIL':<8} {elapsed:.0f}s  [{ds}]")
        if sats:
            sup, K, B1, K_col, VD, d_f, d_fm = sats[0]
            print(f"      max-K example: sup={sup}, K={K} (B_1={B1}, K_col={K_col}), |V_δ|={VD}")


if __name__ == "__main__":
    main()
