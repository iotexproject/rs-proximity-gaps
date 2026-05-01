"""g3_K_bound_64_16_quick.py — predict K bound at (64, 16) deployment scale.

At (64, 16): n_1 = 32, k_1 = 8, w_J(L_1) = 16. M_max(L_1) = n_1 - s + 1.

For BCIKS at L_1: s_1 satisfies n_1 - sqrt(k_1·n_1) = ?
sqrt(8 × 32) = sqrt(256) = 16. So s_1 = 16, M_max = 32 - 16 + 1 = 17.

Predicted K ≤ n_1 - s + 2 = 18 at (64, 16).

Quick test: pick a few all-odd 3-pos supports + a Pattern A' (no j ≡ 1 mod 4)
and verify K stays bounded.
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
        i = int(T[0])
        idxs = [int(t) for t in T]
        # k_2 = 4: linear interpolation through 4 points
        # Use Lagrange basis. For each "k" not in T, compute c_k coefs.
        T_set = set(idxs)
        kpairs = []
        for k in range(n2):
            if k in T_set: continue
            # Lagrange basis at T → value at k
            yk = int(L2_arr[k])
            coeffs = []
            for ii_idx, ii in enumerate(idxs):
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


def per_alpha2_count_general_k(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    """General-k version: for each T (k_2 info set) and α_2,
    count extras (= positions z ∉ T where polynomial agreement holds)."""
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]; fo = [int(x) for x in fold1_o]
    for T_idx, idxs, kpairs in lagrange_pairs:
        always_count = 0; targets = []
        for k, coeffs in kpairs:
            # Predicted value at k = sum_{ii ∈ T} c_ii · fold²[ii]
            # fold²[ii] = fe[ii] + α_2 · fo[ii]
            # Predicted = sum c · fe[ii] + α_2 · sum c · fo[ii]
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
    w_J_L0, w_J_L2 = 32, 8

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    print(f"info_sets_n2 size: {len(info_sets_n2)}")
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    # Test all-odd supports in [k_0, n_0-1] = [16, 63]
    test_sups = [
        (17, 19, 21),  # all ≡ 1 mod 4
        (17, 19, 23),  # mixed
        (19, 21, 23),  # all ≡ 3 mod 4
        (17, 19, 31),  # span larger range
        (33, 35, 47),  # higher positions
    ]

    print(f"\n=== K bound at (64, 16) deployment scale, q={p} ===")
    print(f"  Predicted K ≤ n_1 - s + 2 = 18")
    print(f"  Each config takes O(p² × 56) operations\n")

    print(f"{'sup':<16} {'(f_e≡0)':<8} {'|V_δ|':<8} {'|B_1|':<6} {'K_col':<6} {'K':<4}")
    print("-"*60)
    for sup in test_sups:
        sup_rng = random.Random(2026 + hash(sup) & 0xFFFFFFFF)
        coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_zero = all(x == 0 for x in f_e)

        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        bad = np.zeros((p, p), dtype=np.int32)
        t0 = time.time()
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            bad[a1, :] = per_alpha2_count_general_k(fold1_e, fold1_o, lagrange_pairs,
                                                     p, n2, k2, w_J_L2)
        elapsed = time.time() - t0
        VD = int(bad.sum())
        row = bad.sum(axis=1); col = bad.sum(axis=0)
        B1 = int((row == p).sum())
        K_col = int((col == p).sum())
        K = B1 + K_col
        print(f"{str(sup):<16} {str(fe_zero):<8} {VD:<8} {B1:<6} {K_col:<6} {K:<4}  ({elapsed:.1f}s)")

    print(f"\nIf max K above ≤ 18: bound K ≤ n_1-s+2 holds at (64, 16).")


if __name__ == "__main__":
    main()
