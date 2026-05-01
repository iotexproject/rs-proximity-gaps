"""g3_pattern_B_verify.py — verify Theorem 0175.B for all-odd supports.

Claim: if supp(f̂) ⊂ {odd indices in [k_0, n_0-1]}, then:
  (1) f_e ≡ 0 on L_1
  (2) fold²(α_1, α_2) = α_1 · g(α_2) where g = (f_o)_e + α_2 (f_o)_o on L_2
  (3) |V_δ| = q + (q−1) · |Bad(g)|
  (4) |Bad(g)| ≤ 9 = n_1 − s_1 + 1 (BCIKS bound for 1-line g on L_1).
"""
import sys, os, random
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


def main():
    p = 97
    n0, k0, R = 32, 8, 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L0, w_J_L1, w_J_L2 = 16, 8, 4

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

    # All-odd 3-pos supports in [k_0, n_0-1] = [8, 31]
    all_odd_sups = [s for s in combinations(range(8, 32), 3)
                    if all(j % 2 == 1 for j in s)]
    print(f"Total all-odd 3-pos supports in [8, 31]: {len(all_odd_sups)}")

    print(f"\n  {'sup':<14} {'f_e≡0?':<8} {'count_g':<8} {'|V_δ|':<6} "
          f"{'predicted':<10} {'match?'}")
    print("  " + "-"*72)

    ok = 0; total = 0
    sample = all_odd_sups[:30]  # first 30

    for sup in sample:
        sup_rng = random.Random(42 + hash(sup) & 0xFFFFFFFF)
        coefs = [sup_rng.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)

        # Check (1): f_e ≡ 0
        fe_zero = all(x == 0 for x in f_e)

        # Now compute |V_δ| directly
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        # Compute g(α_2) on L_2 for f_o (just one α_1 = 1)
        # fold¹(α_1=1) = f_e + f_o = f_o (since f_e ≡ 0)
        fold1 = fo_arr.tolist()
        fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
        fe_l2 = np.array(fold1_e, dtype=np.int64)
        fo_l2 = np.array(fold1_o, dtype=np.int64)

        # Count |Bad(g)| = #{α_2 : d_2(fold²(1, α_2)) ≤ w_J_L2}
        count_g = 0
        for a2 in range(p):
            fold2 = (fe_l2 + a2 * fo_l2) % p
            extras = batched_extras(info_sets_n2, fold2, L2_arr, D2, inv_D2, p)
            d2 = n2 - k2 - int(extras.max())
            if d2 <= w_J_L2:
                count_g += 1

        # Predicted |V_δ| = q + (q-1) * count_g (assuming f_e ≡ 0)
        predicted = p + (p - 1) * count_g

        # Compute actual |V_δ| (sweep over all (α_1, α_2))
        actual = 0
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            fe_l2_a = np.array(fold1_e, dtype=np.int64)
            fo_l2_a = np.array(fold1_o, dtype=np.int64)
            for a2 in range(p):
                fold2 = (fe_l2_a + a2 * fo_l2_a) % p
                extras = batched_extras(info_sets_n2, fold2, L2_arr, D2, inv_D2, p)
                d2 = n2 - k2 - int(extras.max())
                if d2 <= w_J_L2:
                    actual += 1

        match = (predicted == actual) and fe_zero
        if match: ok += 1
        total += 1
        flag = "OK" if match else "FAIL"
        print(f"  {str(sup):<14} {str(fe_zero):<8} {count_g:<8} {actual:<6} "
              f"{predicted:<10} {flag}")

    print(f"\n  Verified: {ok}/{total} all-odd supports match Theorem 0175.B")

    # Also: does count_g ≤ 9 hold?
    print(f"\n  (M_max bound check pending across all 30 samples)")


if __name__ == "__main__":
    main()
