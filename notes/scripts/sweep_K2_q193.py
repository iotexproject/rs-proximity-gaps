"""sweep_K2_q193.py — sweep random K=2 above-J f's at q=193 (R=2).

Compare to q=97 results:
  q=97 K=2 max tie: 0.4477 (audited (18,8) breach with |E|=7)
  q=97 K=2 max tie: 0.4476 (|E|=8 case T1=(0,1,6), T2=(0,2,5))

Predict at q=193: drops similarly to K=1 (97→257: 0.4490→0.382).
"""
from __future__ import annotations
import sys, os, random, time
from itertools import combinations, product
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 193
N0 = 32
K0 = 8
R = 2
W_R = 3

import probe_step5_n32_studio
probe_step5_n32_studio.P = P
probe_step5_n32_studio.N0 = N0
probe_step5_n32_studio.K0 = K0

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, matvec, gauss_rank
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    return [sum(fhat[k] * pow(L[i], k, p) for k in range(len(fhat))) % p for i in range(len(L))]


CHAIN = setup_chain(P, N0, K0, R=R)


def construct_K2_psi_in_U(rng, p, chain, H_R, n_R):
    """Construct K=2 above-J f via psi_b ∈ 2-dim U structure."""
    for _ in range(20):
        T1 = tuple(sorted(rng.sample(range(n_R), W_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            avail = [j for j in range(n_R) if j not in T1]
            if len(avail) < W_R: continue
            T2 = tuple(sorted(rng.sample(avail, W_R)))
        else:
            shared = rng.choice(list(T1))
            others = [j for j in range(n_R) if j not in T1]
            if len(others) < W_R - 1: continue
            T2 = tuple(sorted([shared] + rng.sample(others, W_R - 1)))
        if T2 == T1 or len(set(T1) & set(T2)) > 1: continue
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1: eps1[j] = rng.randrange(1, p)
        for j in T2: eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2: continue
        c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
        msg = [rng.randrange(p) for _ in range(K0)]
        # Construct fhat with psi_b in U
        K_R = chain[R][1]  # k_R = 2
        M = n_R - K_R  # = 8 - 2 = 6
        fhat = list(msg) + [0] * (N0 - K0)
        for b in product([0, 1], repeat=R):
            b_int = sum(b[r] * (2 ** r) for r in range(R))
            c0, c1 = c[b]
            for i in range(M):
                pos = (K_R + i) * (2 ** R) + b_int
                if pos < N0:
                    fhat[pos] = (c0 * u1[i] + c1 * u2[i]) % p
        L0 = chain[0][0]
        f = evaluate_dft(fhat, L0, p)
        return f, T1, T2
    return None, None, None


def fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1):
    extras = batched_extras(info_sets_arr, fold1_arr, L1_arr, D1, inv_D1, p)
    return n1 - k1 - int(extras.max())


def fast_d2(fold2, L2, p):
    n2 = len(L2)
    max_agree = 0
    for i, j in combinations(range(n2), 2):
        xi, xj = L2[i], L2[j]
        yi, yj = fold2[i] % p, fold2[j] % p
        if xi == xj: continue
        slope = ((yj - yi) * pow((xj - xi) % p, p - 2, p)) % p
        intercept = (yi - slope * xi) % p
        agree = sum(1 for k in range(n2) if (intercept + slope * L2[k]) % p == fold2[k] % p)
        if agree > max_agree: max_agree = agree
    return n2 - max_agree


def compute_tie_with_above_J_check(f, chain, p):
    """Compute tie_upper and check above-J via Lemma 1 (min d_1 ≥ 9)."""
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    L2, k2, _ = chain[2]
    n1, n2 = len(L1), len(L2)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_list = list(L2)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    sum_tie = 0.0
    d1_dist = Counter()
    min_d1_nonzero = n1
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d1 = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d1_dist[d1] += 1
        if a1 != 0 and d1 < min_d1_nonzero:
            min_d1_nonzero = d1
        fold1 = fold1_arr.tolist()
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2 = fast_d2(fold2, L2_list, p)
            P_B = 1.0 - d2 / n2
            P_A_ub = 1.0 - d1 / n1
            sum_tie += max(P_A_ub, P_B)
    above_J_via_lemma1 = (2 * min_d1_nonzero) > 16
    return sum_tie / (p*p), d1_dist, min_d1_nonzero, above_J_via_lemma1


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)

    print(f"=== K=2 random above-J at q={p} ===")
    print(f"Each tie eval: {p}^2 = {p**2:,} tuples, ~10s")

    rng = random.Random(2026)
    n_tested = 0
    n_above_J = 0
    max_tie_above_J = 0.0
    max_case = None
    target = 20
    t0 = time.time()
    while n_above_J < target and n_tested < 200:
        n_tested += 1
        f, T1, T2 = construct_K2_psi_in_U(rng, p, chain, H_R, n_R)
        if f is None:
            continue
        tie, d1d, min_d1, above_J = compute_tie_with_above_J_check(f, chain, p)
        status = "above-J" if above_J else "below-J"
        elapsed = time.time() - t0
        print(f"  attempt {n_tested}: {status} (min d_1={min_d1}), tie={tie:.4f}, T1={T1}, T2={T2}, elapsed={elapsed:.0f}s")
        if above_J:
            n_above_J += 1
            if tie > max_tie_above_J:
                max_tie_above_J = tie
                max_case = (T1, T2, d1d, tie)

    print(f"\n=== Summary ===")
    print(f"  Tested: {n_tested} K=2 candidates")
    print(f"  Above-J certified (Lemma 1): {n_above_J}")
    print(f"  Max tie among above-J: {max_tie_above_J:.4f}")
    print(f"  Compare q=97 K=2 max: 0.4477 (audited)")
    print(f"  K=1 worst case at q={p}: ~0.32-0.38")
    if max_case:
        T1, T2, d1d, tie = max_case
        print(f"  Worst case: T1={T1}, T2={T2}, d_1 dist top 5: {dict(sorted(d1d.items())[:5])}")


if __name__ == "__main__":
    main()
