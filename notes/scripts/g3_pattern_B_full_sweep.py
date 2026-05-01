"""g3_pattern_B_full_sweep.py — verify count_g ≤ 9 across ALL 220 all-odd
3-pos sparse supports at q=97, (32,8). Fast: only computes count_g
(no sweep over α_1, since fold²(α_1, α_2) = α_1·g(α_2)).
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


def main():
    p = 97
    n0, k0, R = 32, 8, 2
    n2, k2 = 8, 2
    w_J_L2 = 4
    n_seeds = 5

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

    all_odd_sups = [s for s in combinations(range(8, 32), 3)
                    if all(j % 2 == 1 for j in s)]
    print(f"All-odd 3-pos supports in [8, 31]: {len(all_odd_sups)}, n_seeds={n_seeds}")

    cnt_dist = Counter()
    max_cnt = 0
    max_examples = []
    for sup in all_odd_sups:
        for seed in range(n_seeds):
            sup_rng = random.Random((42 + seed) ^ (hash(sup) & 0xFFFFFFFF))
            coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p

            f = evaluate_dft(fhat, L0, p)
            f_e, f_o = even_odd_parts(f, L0, p)
            # f_e should be ≡ 0; assert
            assert all(x == 0 for x in f_e), f"f_e not zero for sup={sup}"

            # g(α_2) = (f_o)_e + α_2·(f_o)_o on L_2
            fold1 = list(f_o)  # since fold¹(α_1=1) = f_o
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            fe_l2 = np.array(fold1_e, dtype=np.int64)
            fo_l2 = np.array(fold1_o, dtype=np.int64)

            count_g = 0
            for a2 in range(p):
                fold2 = (fe_l2 + a2 * fo_l2) % p
                extras = batched_extras(info_sets_n2, fold2, L2_arr, D2, inv_D2, p)
                d2 = n2 - k2 - int(extras.max())
                if d2 <= w_J_L2:
                    count_g += 1
            cnt_dist[count_g] += 1
            if count_g > max_cnt:
                max_cnt = count_g
                max_examples = [(sup, seed, coefs)]
            elif count_g == max_cnt:
                if len(max_examples) < 5:
                    max_examples.append((sup, seed, coefs))

    print(f"\n  count_g distribution across {len(all_odd_sups)*n_seeds} samples:")
    for cnt, n in sorted(cnt_dist.items()):
        flag = " <-- max" if cnt == max_cnt else ""
        flag += f" → |V_δ| = q + {cnt}(q-1) = {p + cnt*(p-1)}"
        print(f"    count_g={cnt}: {n} samples{flag}")

    print(f"\n  Max count_g observed: {max_cnt}")
    print(f"  Predicted bound n_1 - s_1 + 1 = 9; bound = {'HOLDS' if max_cnt <= 9 else 'VIOLATED!'}")
    print(f"  Max |V_δ| = q + {max_cnt}(q-1) = {p + max_cnt*(p-1)}")
    if max_cnt == 9:
        print(f"  Examples hitting count_g = 9 (= 10q - 9 ceiling):")
        for sup, seed, coefs in max_examples:
            print(f"    sup={sup} (seed {seed})")


if __name__ == "__main__":
    main()
