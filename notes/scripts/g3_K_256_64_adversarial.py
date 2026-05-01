"""g3_K_256_64_adversarial.py — adversarial K test at (256, 64) above-J Reverse.

Mirror of g3_K_128_32_adversarial.py but at (256, 64).

Per Theorem 0187 + Conjecture E: predicted K ≤ n_2/gcd(r, n_2) + 2.
Worst case (r=1): K ≤ 66. Empirical "9 universal" at (32, 8), (128, 32) suggests
maybe much tighter at (256, 64) too.

Filter: above-J at L_0 (positions ≥ k_0 = 64) + Reverse Pattern (mod 4 ∈ {2, 3}).
Track non-degenerate K (excluding c = 0 cases that give K = q).
"""
import sys, os, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain, even_odd_parts
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
    p = 257
    n0, k0 = 256, 64
    n2, k2 = 64, 16
    w_J_L2 = n2 - int(round(np.sqrt(k2 * n2)))  # = 32

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    rev_pos = [j for j in range(k0, n0) if j % 4 in (2, 3)]
    print(f"Above-J Reverse positions: {len(rev_pos)} (out of {n0})")

    rng = random.Random(2026)
    sample_size = 5000
    info_rng = np.random.default_rng(2027)
    sample = []; seen = set()
    while len(sample) < sample_size:
        T = tuple(sorted(info_rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)
    print(f"Sample at L_2: {len(sample)} of C(64, 16)")

    n_triples = 200
    all_triples = list(combinations(rev_pos, 3))
    rng.shuffle(all_triples)
    test_triples = all_triples[:n_triples]
    print(f"Testing {len(test_triples)} above-J Reverse triples\n")

    K_distribution = {}
    high_K_supports = []
    extreme_K_nondeg = -1
    extreme_sup = None

    t0 = time.time()
    for idx, sup in enumerate(test_triples):
        coefs = [(idx*7 + 11) % (p-1) + 1, (idx*13 + 17) % (p-1) + 1, (idx*19 + 23) % (p-1) + 1]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)
        c_arr = np.array(fe_o, dtype=np.int64)
        d_arr = np.array(fo_o, dtype=np.int64)

        # Check degeneracy: c = 0 → pencil = α·d → K = q (degenerate column)
        c_is_zero = (c_arr == 0).all()

        bad_count = 0
        bad_alphas = []
        for alpha in range(p):
            h = (c_arr + alpha * d_arr) % p
            ext = batched_extras(info_arr, h, L2_arr, D2, inv_D2, p)
            d = n2 - k2 - int(ext.max())
            if d <= w_J_L2:
                bad_count += 1
                bad_alphas.append(alpha)

        K = bad_count
        K_distribution[K] = K_distribution.get(K, 0) + 1
        if not c_is_zero and K > extreme_K_nondeg:
            extreme_K_nondeg = K
            extreme_sup = sup
        if K > 18 and not c_is_zero:
            high_K_supports.append((sup, K, bad_alphas[:5]))

        if idx % 50 == 0:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            eta = (len(test_triples) - idx - 1) / rate
            print(f"  [{idx+1}/{len(test_triples)}] non-deg max K = {extreme_K_nondeg}; ETA {eta:.0f}s")

    print(f"\nTotal elapsed: {time.time()-t0:.0f}s")
    print(f"\nK distribution (all): {sorted(K_distribution.items())}")
    print(f"Max non-degenerate K = {extreme_K_nondeg} at sup={extreme_sup}")
    if high_K_supports:
        print(f"\nNon-degenerate supports with K > 18:")
        for sup, K, alphas in high_K_supports[:10]:
            print(f"  {sup}: K = {K}, sample bad α: {alphas}")
    else:
        print("\n** NO NON-DEGENERATE SUPPORT WITH K > 18 — Conjecture E + Theorem 0187 prediction holds **")


if __name__ == "__main__":
    main()
