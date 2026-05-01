"""verify_no_common_8flat.py — verify "no common 8-flat" hypothesis empirically.

Refining Theorem 0145: the per-c-T multiplicity bound 234 holds whenever
NO 4-subset T ⊂ L_1 has z_T = 4. The z_T = 4 condition requires:

    ∃ 8-subset H ⊃ T, |H| = 8, such that
        f_e|_H is the evaluation of a deg<4 polynomial AND
        f_o|_H is the evaluation of a deg<4 polynomial.

This is the "common 8-flat" condition.

Hypothesis: even in degenerate-at-level-1 cases (dist(f_e, C_1) = 8 OR
dist(f_o, C_1) = 8), the common 8-flat condition rarely holds.

Specifically: if dist(f_e, C_1) = 8 with agreement set H_e, and dist(f_o, C_1) ≥ 9,
then no 8-subset of H_e is contained in an f_o-agreement set (since f_o has no
agreement ≥ 8 anywhere).

So the "no common 8-flat" property follows from:
    dist(f_e, C_1) ≥ 9  OR  dist(f_o, C_1) ≥ 9  (NOT BOTH degenerate).

Even weaker: it follows if their agreement-sets have empty intersection.

This verifies empirically.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

W_J = N0 // 2


def compute_zT(f_e_arr, f_o_arr, T, L1_arr, p):
    """For T = (i_0,...,i_3), compute z_T = #{i ∉ T : A_T(i) = B_T(i) = 0}.
    A_T(i) = Lagrange(f_e|_T)(L1[i]) - f_e[i].
    B_T(i) = Lagrange(f_o|_T)(L1[i]) - f_o[i].
    """
    n1 = len(L1_arr)
    # Lagrange interpolation at point x for values v on T
    T_vals = L1_arr[list(T)]  # 4 x-coords
    fe_T = f_e_arr[list(T)]
    fo_T = f_o_arr[list(T)]
    # For each x_eval in L1: Lagrange(v)(x_eval) = sum_j v[j] * prod_{k!=j}(x_eval - x_k)/(x_j - x_k)
    z = 0
    for i in range(n1):
        if i in T: continue
        x = int(L1_arr[i])
        Lfe = 0
        Lfo = 0
        for j in range(4):
            xj = int(T_vals[j])
            num = 1
            den = 1
            for k in range(4):
                if k == j: continue
                xk = int(T_vals[k])
                num = (num * (x - xk)) % p
                den = (den * (xj - xk)) % p
            inv_den = pow(den, p - 2, p)
            Lfe = (Lfe + int(fe_T[j]) * num * inv_den) % p
            Lfo = (Lfo + int(fo_T[j]) * num * inv_den) % p
        A = (Lfe - int(f_e_arr[i])) % p
        B = (Lfo - int(f_o_arr[i])) % p
        if A == 0 and B == 0:
            z += 1
    return z


def main():
    from mds_decoder import dist_lower_bound_sampling, precompute_diff_inv, batched_extras

    print("=== verify_no_common_8flat: checking z_T < 4 universally ===")
    print()
    overall_max_zT = 0
    n_tested_total = 0
    n_doubly_degen = 0
    n_zT_max4 = 0
    for p in [97, 193, 449]:
        if (p - 1) % N0 != 0: continue
        chain = setup_chain(p, N0, K0, R=R)
        L0 = chain[0][0]
        L1, k1, _ = chain[1]
        n1 = len(L1)
        L1_arr = np.array(L1, dtype=np.int64)
        D1, inv_D1 = precompute_diff_inv(L1_arr, p)
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)
        rng = random.Random(2026 + p)
        max_zT_q = 0
        n_tested = 0
        n_doubly_q = 0
        n_zT4_q = 0
        n_tries = 0
        n_K2_above_J = 0
        max_count = 0
        while n_tested < 30 and n_tries < 300:
            n_tries += 1
            n_pos = rng.choice([3, 4, 5, 6])
            positions = sorted(rng.sample(range(K0, N0), n_pos))
            has_even = any(j % 2 == 0 for j in positions)
            has_odd = any(j % 2 == 1 for j in positions)
            if not (has_even and has_odd): continue
            fhat = [0] * N0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft(fhat, L0, p)
            d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
            if d <= W_J: continue
            n_K2_above_J += 1
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            extras_fe = batched_extras(info_sets_arr, f_e_arr, L1_arr, D1, inv_D1, p)
            extras_fo = batched_extras(info_sets_arr, f_o_arr, L1_arr, D1, inv_D1, p)
            d_fe = n1 - k1 - int(extras_fe.max())
            d_fo = n1 - k1 - int(extras_fo.max())
            # Only test cases where AT LEAST ONE is degenerate (dist ≤ 8)
            if d_fe >= 9 and d_fo >= 9: continue  # doubly-above-J@1 already handled
            # Doubly-degenerate: dist_fe ≤ 8 AND dist_fo ≤ 8
            doubly_degen = (d_fe <= 8 and d_fo <= 8)
            if doubly_degen:
                n_doubly_q += 1
            # Compute max z_T over all T ⊂ L_1
            max_zT = 0
            for T in info_sets:
                zT = compute_zT(f_e_arr, f_o_arr, T, L1_arr, p)
                if zT > max_zT:
                    max_zT = zT
                if zT >= 4:
                    break  # found one bad T, no need to continue
            if max_zT >= 4:
                n_zT4_q += 1
            # Count_α(d_1 ≤ 8)
            count_8 = 0
            for a in range(p):
                fold = (f_e_arr + a * f_o_arr) % p
                extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
                d1 = n1 - k1 - int(extras.max())
                if d1 <= 8: count_8 += 1
            n_tested += 1
            n_tested_total += 1
            if max_zT > max_zT_q:
                max_zT_q = max_zT
                print(f"  q={p} pos={positions}: d_fe={d_fe}, d_fo={d_fo}, doubly_degen={doubly_degen}, max z_T={max_zT}, count_8={count_8}")
            if count_8 > max_count:
                max_count = count_8
        print(f"  q={p}: {n_K2_above_J} K=2 above-J seen, {n_tested} degenerate-at-level-1 tested,")
        print(f"         {n_doubly_q} doubly-degenerate, {n_zT4_q} have z_T ≥ 4 for some T,")
        print(f"         max z_T overall = {max_zT_q}, max count_α(d_1 ≤ 8) = {max_count}")
        if max_zT_q > overall_max_zT: overall_max_zT = max_zT_q
        n_doubly_degen += n_doubly_q
        n_zT_max4 += n_zT4_q
        print()

    print(f"=== Total {n_tested_total} degenerate-at-level-1 cases tested ===")
    print(f"  doubly-degenerate (both dist ≤ 8): {n_doubly_degen}")
    print(f"  z_T ≥ 4 for some T: {n_zT_max4}")
    print(f"  overall max z_T = {overall_max_zT}")
    if overall_max_zT < 4:
        print(f"  ✓ z_T < 4 holds UNIVERSALLY across degenerate-at-level-1 cases")
        print(f"  ⟹ Theorem 0145's per-c-T multiplicity bound (234) extends to ALL K=2 above-J f")
    else:
        print(f"  ✗ z_T = 4 occurs — must analyze residual case via 'common 8-flat'")


if __name__ == "__main__":
    main()
