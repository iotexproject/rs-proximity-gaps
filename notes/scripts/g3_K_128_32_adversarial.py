"""g3_K_128_32_adversarial.py — adversarially search for K > 10 at (128, 32) Reverse.

Prior 80-support sweep gave K_dist {1: 54, 2: 23, 3: 1, 10: 1, -1: 1}.
Question: is the "10" cap structural, or just under-sampling of triples?

Strategy:
- Enumerate many MORE Reverse Pattern 3-pos supports (5000+ triples)
- Use larger info_set sample for tighter bound on per-triple K
- Track top-K candidates

If K stuck at ≤ 10 across 5000+ supports, "9 universal" hypothesis strengthens.
If K reaches ≥ 11 anywhere, find counterexample.
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
    n0, k0 = 128, 32
    n2, k2 = 32, 8
    w_J_L2 = n2 - int(round(np.sqrt(k2 * n2)))  # = 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    # Reverse positions (mod 4 in {2, 3}) AND above-J at L_0 (positions ≥ k_0 = 32)
    # This restricts to "doubly recursive above-J" relevant supports.
    rev_pos = [j for j in range(k0, n0) if j % 4 in (2, 3)]
    print(f"Reverse positions in L_0 (above-J: ≥ k_0 = {k0}): {len(rev_pos)} (out of {n0})")

    rng = random.Random(2026)
    sample_size = 5000  # for L_2 info_sets
    info_rng = np.random.default_rng(2027)
    sample = []; seen = set()
    while len(sample) < sample_size:
        T = tuple(sorted(info_rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)
    print(f"Sample at L_2: {len(sample)} of C(32, 8) = 10518300 (~5·10^-4)")

    # Enumerate many Reverse triples
    n_triples = 800
    all_triples = list(combinations(rev_pos, 3))
    rng.shuffle(all_triples)
    test_triples = all_triples[:n_triples]
    print(f"Testing {len(test_triples)} Reverse triples\n")

    K_distribution = {}
    high_K_supports = []  # K > 10
    extreme_K = -1
    extreme_sup = None

    t0 = time.time()
    for idx, sup in enumerate(test_triples):
        # Use varied coefs
        coefs = [(idx*7 + 11) % (p-1) + 1, (idx*13 + 17) % (p-1) + 1, (idx*19 + 23) % (p-1) + 1]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)
        c_arr = np.array(fe_o, dtype=np.int64)
        d_arr = np.array(fo_o, dtype=np.int64)

        # Count bad α (full enumeration)
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
        if K > extreme_K:
            extreme_K = K
            extreme_sup = sup
        if K > 10:
            high_K_supports.append((sup, K, bad_alphas[:5]))

        if idx % 200 == 0:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            eta = (len(test_triples) - idx - 1) / rate
            print(f"  [{idx+1}/{len(test_triples)}] max K so far = {extreme_K} (sup={extreme_sup}); ETA {eta:.0f}s")

    print(f"\nTotal elapsed: {time.time()-t0:.0f}s")
    print(f"\nK distribution: {sorted(K_distribution.items())}")
    print(f"Max K observed: {extreme_K} at sup={extreme_sup}")
    if high_K_supports:
        print(f"\nSupports with K > 10:")
        for sup, K, alphas in high_K_supports[:10]:
            print(f"  {sup}: K = {K}, sample bad α: {alphas}")
    else:
        print("\n** NO SUPPORT FOUND WITH K > 10 — '9 universal' hypothesis strengthens **")


if __name__ == "__main__":
    main()
