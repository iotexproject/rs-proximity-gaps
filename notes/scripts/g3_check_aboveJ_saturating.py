"""g3_check_aboveJ_saturating.py — for the 25 all-odd supports that gave
count_g = 97 (|V_δ| = q²), check if they are above-J at L_0.

Hypothesis: they're NOT above-J — the saturation only happens for f close to RS_{k_0}.
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
    w_J_L0 = 16; w_J_L2 = 4
    n_seeds = 5

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

    # Sampled info sets at L_0 for above-J approximation (30K is plenty)
    rng_l0 = np.random.default_rng(2026)
    all_T_n0 = list(combinations(range(n0), k0))
    idx = rng_l0.choice(len(all_T_n0), size=30000, replace=False)
    info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)
    print(f"Sampled info_sets_n0 size: {len(info_sets_n0)} of {len(all_T_n0)}")

    all_odd_sups = [s for s in combinations(range(8, 32), 3)
                    if all(j % 2 == 1 for j in s)]

    # Categorize by mod-4 uniformity
    cats = {'mod4=1': [], 'mod4=3': [], 'mixed-1-3': []}
    for s in all_odd_sups:
        m4 = set(j % 4 for j in s)
        if m4 == {1}: cats['mod4=1'].append(s)
        elif m4 == {3}: cats['mod4=3'].append(s)
        else: cats['mixed-1-3'].append(s)
    print(f"Categories: mod4=1: {len(cats['mod4=1'])}, "
          f"mod4=3: {len(cats['mod4=3'])}, mixed-1-3: {len(cats['mixed-1-3'])}")

    # For each, count count_g distribution + above-J status
    print(f"\n{'category':<14} {'count_g distribution':<35} {'aboveJ-saturating':<20}")
    print("-"*80)

    for cat_name, sups in cats.items():
        cnt_dist = Counter()
        aboveJ_sat = 0
        belowJ_sat = 0
        for sup in sups:
            for seed in range(n_seeds):
                sup_rng = random.Random((42 + seed) ^ (hash(sup) & 0xFFFFFFFF))
                coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
                fhat = [0]*n0
                for j, c in zip(sup, coefs): fhat[j] = c % p

                f = evaluate_dft(fhat, L0, p)
                f_arr = np.array(f, dtype=np.int64)
                ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
                d_f = n0 - k0 - int(ext.max())

                f_e, f_o = even_odd_parts(f, L0, p)
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
                if count_g == p:
                    if d_f > w_J_L0: aboveJ_sat += 1
                    else: belowJ_sat += 1
        ds = ', '.join(f"{c}:{n}" for c, n in sorted(cnt_dist.items())[:8])
        print(f"{cat_name:<14} {ds[:33]:<35} aboveJ={aboveJ_sat}, belowJ={belowJ_sat}")

    print(f"\n=== Saturating examples (count_g = q) ===")
    print(f"  Looking at uniform mod4=1 case in detail...")
    for sup in cats['mod4=1'][:5]:
        for seed in range(n_seeds):
            sup_rng = random.Random((42 + seed) ^ (hash(sup) & 0xFFFFFFFF))
            coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p
            f = evaluate_dft(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
            d_f = n0 - k0 - int(ext.max())

            f_e, f_o = even_odd_parts(f, L0, p)
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
            if count_g == p:
                aboveJ = "ABOVE-J" if d_f > w_J_L0 else "below-J"
                print(f"  sup={sup} seed={seed} d_f={d_f} ({aboveJ}) coefs={coefs} count_g=97")


if __name__ == "__main__":
    main()
