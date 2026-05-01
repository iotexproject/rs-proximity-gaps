"""g3_pattern_B_64_16.py — verify Pattern B Theorem 0175.B at (64, 16)
deployment scale. Checks |V_δ| = q + (q-1)·count_g and predicted bound.
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


def main():
    p = 193   # smallest q ≡ 1 mod 64
    n0, k0, R = 64, 16, 2
    n1, k1 = 32, 8
    n2, k2 = 16, 4
    w_J_L0, w_J_L1, w_J_L2 = 32, 16, 8

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    print(f"info_sets_n2 size: {len(info_sets_n2)}")

    # C(64, 16) is too large to enumerate. Sample directly.
    rng_l0 = np.random.default_rng(2026)
    n_samples_l0 = 30000
    info_sets_l0 = []
    seen = set()
    while len(info_sets_l0) < n_samples_l0:
        T = tuple(sorted(rng_l0.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen:
            seen.add(T)
            info_sets_l0.append(T)
    info_sets_n0 = np.array(info_sets_l0, dtype=np.int64)
    print(f"info_sets_n0 sampled: {len(info_sets_n0)}")

    # All-odd 3-pos supports in [k_0, n_0-1] = [16, 63]
    all_odd_sups = [s for s in combinations(range(16, 64), 3)
                    if all(j % 2 == 1 for j in s)]
    print(f"All-odd 3-pos supports in [16, 63]: {len(all_odd_sups)}")
    n_seeds = 2

    print(f"\nSampling {n_seeds} coef seeds per support, q={p}, (64, 16)...")

    cnt_dist = Counter()
    aboveJ_max_count_g = 0
    aboveJ_max_examples = []
    n_aboveJ = 0
    n_below = 0

    sample = random.Random(2026).sample(all_odd_sups, 200)
    t0 = time.time()
    for sup_idx, sup in enumerate(sample):
        for seed in range(n_seeds):
            sup_rng = random.Random((42 + seed) ^ (hash(sup) & 0xFFFFFFFF))
            coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p

            f = evaluate_dft(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
            d_f = n0 - k0 - int(ext.max())
            aboveJ = (d_f > w_J_L0)

            f_e, f_o = even_odd_parts(f, L0, p)
            assert all(x == 0 for x in f_e), f"f_e not zero for sup={sup}"

            fold1 = list(f_o)
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            fe_l2 = np.array(fold1_e, dtype=np.int64)
            fo_l2 = np.array(fold1_o, dtype=np.int64)

            count_g = 0
            for a2 in range(p):
                fold2 = (fe_l2 + a2 * fo_l2) % p
                extras = batched_extras(info_sets_n2, fold2, L2_arr, D2, inv_D2, p)
                d2 = n2 - k2 - int(extras.max())
                if d2 <= w_J_L2: count_g += 1
            cnt_dist[count_g] += 1
            if aboveJ:
                n_aboveJ += 1
                if count_g > aboveJ_max_count_g:
                    aboveJ_max_count_g = count_g
                    aboveJ_max_examples = [(sup, seed, count_g)]
                elif count_g == aboveJ_max_count_g and len(aboveJ_max_examples) < 5:
                    aboveJ_max_examples.append((sup, seed, count_g))
            else:
                n_below += 1

        if (sup_idx + 1) % 20 == 0:
            print(f"  [{sup_idx+1}/{len(sample)}] aboveJ={n_aboveJ}, max count_g aboveJ={aboveJ_max_count_g}, elapsed: {time.time()-t0:.0f}s")

    print(f"\n=== Done in {time.time()-t0:.0f}s ===")
    print(f"  Total samples: {len(sample) * n_seeds}")
    print(f"  Above-J: {n_aboveJ}, below-J: {n_below}")
    print(f"  Above-J max count_g: {aboveJ_max_count_g}")
    print(f"  → max |V_δ| = q + {aboveJ_max_count_g}·(q-1) = {p + aboveJ_max_count_g*(p-1)}")
    print(f"  → ratio = max |V_δ| / q = {(p + aboveJ_max_count_g*(p-1))/p:.2f}")

    print(f"\n  count_g distribution:")
    for cnt, n in sorted(cnt_dist.items()):
        print(f"    count_g={cnt}: {n}")


if __name__ == "__main__":
    main()
