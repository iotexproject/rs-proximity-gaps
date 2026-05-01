"""g3_K_bound_q_universal.py — verify Theorem 178 (K = |B_1| + K_col ≤ 10)
across q ∈ {97, 193, 449, 1153} on a sample of 3-pos sparse supports.
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


def sweep_q(p, n0, k0, R, n2, k2, w_J_L0, w_J_L2, sample_supports, n_seeds):
    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    rng_l0 = np.random.default_rng(2026)
    # Sample without materializing full list
    sample_size = 30000
    sampled = []
    seen = set()
    while len(sampled) < sample_size:
        T = tuple(sorted(rng_l0.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen:
            seen.add(T)
            sampled.append(T)
    info_sets_n0 = np.array(sampled, dtype=np.int64)

    K_dist = Counter()
    max_K = 0
    max_VD = 0
    n_aboveJ = 0
    t0 = time.time()
    for sup_idx, sup in enumerate(sample_supports):
        for seed in range(n_seeds):
            sup_rng = random.Random((42 + seed) ^ (hash(sup) & 0xFFFFFFFF))
            coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p

            f = evaluate_dft(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
            d_f = n0 - k0 - int(ext.max())
            if d_f <= w_J_L0: continue
            n_aboveJ += 1

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
            row = bad.sum(axis=1); col = bad.sum(axis=0)
            B1 = int((row == p).sum())
            K_col = int((col == p).sum())
            K = B1 + K_col
            K_dist[K] += 1
            max_K = max(max_K, K)
            max_VD = max(max_VD, VD)
    return max_K, max_VD, K_dist, n_aboveJ, time.time() - t0


def main():
    n0, k0, R = 32, 8, 2
    n2, k2 = 8, 2
    w_J_L0, w_J_L2 = 16, 4

    all_supports = list(combinations(range(8, 32), 3))
    # Use fixed sample for reproducibility
    sample_supports = random.Random(2026).sample(all_supports, 100)

    primes = [97, 193, 449, 1153]
    print(f"=== K = |B_1| + K_col bound across q ∈ {primes} ===")
    print(f"  Sample: 100 supports × 2 seeds at each q = 200 configs each")
    print(f"  Predicted bound: K ≤ 10 = n_1 - s + 2\n")

    print(f"{'q':<6} {'aboveJ':<7} {'max K':<7} {'max |V_δ|':<10} {'(=10q-9?)':<10} {'elapsed':<8} {'K dist'}")
    print("-"*100)
    for p in primes:
        max_K, max_VD, K_dist, n_aboveJ, elapsed = sweep_q(
            p, n0, k0, R, n2, k2, w_J_L0, w_J_L2, sample_supports, 2)
        is_10q9 = (max_VD == 10*p - 9)
        ds = ", ".join(f"K{k}:{n}" for k, n in sorted(K_dist.items()))
        print(f"{p:<6} {n_aboveJ:<7} {max_K:<7} {max_VD:<10} {str(is_10q9):<10} {elapsed:<.0f}s    {ds[:60]}")


if __name__ == "__main__":
    main()
