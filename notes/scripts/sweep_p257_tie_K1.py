"""sweep_p257_tie_K1.py — Test K=1 leader pattern at q=257 (larger q than toy).

Goal: confirm tie_upper(K=1 leader) ~ 7/16 + O(1/q) holds at q=257.

At q=97: tie_upper(K=1 leader (15,23) coefs (10,17)) = 0.4490 (= 7/16 + 5/(4q)).
At q=257: predicted = 7/16 + O(1/257) ~ 0.443.

Chain: n_0=32, k_0=8, R=2 (same as toy). q=257 (n_0=32 divides q-1=256 ✓).
Each tie_upper eval: 257^2 = 66049 (α_1, α_2) pairs, ~280s with fast decoder.
"""
from __future__ import annotations
import sys, os, time
from itertools import combinations
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Override P at the probe_step5 module level
import probe_step5_n32_studio
probe_step5_n32_studio.P = 257  # Override

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


P = 257
N0 = 32
K0 = 8
R = 2

def evaluate_dft(fhat, L, p):
    return [sum(fhat[k] * pow(L[i], k, p) for k in range(len(fhat))) % p for i in range(len(L))]


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


def compute_tie_robust(f, chain, p):
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

    sum_PB = 0.0
    sum_tie = 0.0
    d1_dist, d2_dist = Counter(), Counter()

    t0 = time.time()
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d1 = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d1_dist[d1] += 1
        fold1 = fold1_arr.tolist()
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2 = fast_d2(fold2, L2_list, p)
            d2_dist[d2] += 1
            P_B = 1.0 - d2 / n2
            P_A_ub = 1.0 - d1 / n1
            sum_PB += P_B
            sum_tie += max(P_A_ub, P_B)
        if (a1 + 1) % 50 == 0:
            elapsed = time.time() - t0
            eta = elapsed * p / (a1 + 1)
            print(f"   α_1 {a1+1}/{p}, elapsed={elapsed:.0f}s, ETA={eta:.0f}s")
    n_pairs = p * p
    return (sum_PB / n_pairs, sum_tie / n_pairs, d1_dist, d2_dist)


def main():
    p = P
    print(f"=== q={p} K=1 leader sweep ===")
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    print(f"Chain dims: n = {[len(c[0]) for c in chain]}, k = {[c[1] for c in chain]}")
    print(f"L_0[0..4] = {L0[:4]}, ω = {L0[1]}")

    # K=1 leader: positions 15, 23 (odd-odd, gap 8 = n_1/2 algebraic family)
    # Pick coefs random — distribution invariant to coef choice for K=1 odd-odd.
    cases = [
        ("(15, 23) coefs (10, 17)", 15, 23, 10, 17),
        ("(14, 22) coefs (1, 27)", 14, 22, 1, 27),  # even-even
        ("(15, 23) coefs (1, 1)", 15, 23, 1, 1),    # different scaling
    ]
    results = []
    for name, p1, p2, c1, c2 in cases:
        print(f"\n--- {name} ---")
        fhat = [0] * N0
        fhat[p1] = c1
        fhat[p2] = c2
        f = evaluate_dft(fhat, L0, p)
        E_PB, tie, d1d, d2d = compute_tie_robust(f, chain, p)
        print(f"  E[P_B] = {E_PB:.4f}, tie_upper = {tie:.4f}")
        print(f"  d_1 dist: {dict(sorted(d1d.items()))}")
        print(f"  d_2 dist: {dict(sorted(d2d.items()))}")
        results.append((name, E_PB, tie))

    print("\n=== Summary ===")
    for name, E_PB, tie in results:
        print(f"  {name}: tie = {tie:.4f}")
    max_tie = max(r[2] for r in results)
    print(f"\nMax tie_upper at q=257: {max_tie:.4f}")
    print(f"Predicted: 7/16 + O(1/q) = {7/16:.4f} + ~{1/p:.4f} = {7/16 + 1/p:.4f}")
    print(f"At q=97 baseline: tie_upper(K=1 leader) = 0.4490")


if __name__ == "__main__":
    main()
