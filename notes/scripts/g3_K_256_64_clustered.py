"""g3_K_256_64_clustered.py — target clustered Reverse triples at (256, 64).

Pattern observed at saturating supports:
- (32, 8): (15, 18, 19) — diffs 3, 1
- (128, 32): (87, 102, 103) — diffs 15, 1
- (256, 64): (139, 154, 155) — diffs 15, 1

So target triples (s_0, s_1, s_2) with s_2 - s_1 = 1 and s_1 - s_0 ∈ {3, 7, 15, 31}.
All in mod 4 ∈ {2, 3} and above-J (≥ k_0 = 64).

Find max K across these clustered triples.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import product
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
    w_J_L2 = n2 - int(round(np.sqrt(k2 * n2)))

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    # Target clustered Reverse triples: (s_0, s_1, s_2) with:
    #   s_0, s_1, s_2 ≥ 64 (above-J at L_0)
    #   s_2 - s_1 = 1
    #   s_1 - s_0 ∈ {3, 7, 15, 31, 63}
    #   all in mod 4 ∈ {2, 3}
    triples = []
    for offset in [3, 7, 15, 31, 63]:
        for s_2 in range(k0 + 1, n0):
            s_1 = s_2 - 1
            s_0 = s_1 - offset
            if s_0 < k0: continue
            if s_2 % 4 not in (2, 3) or s_1 % 4 not in (2, 3) or s_0 % 4 not in (2, 3): continue
            triples.append((s_0, s_1, s_2))
    triples = sorted(set(triples))
    print(f"Targeted clustered triples: {len(triples)}")
    print(f"Sample triples: {triples[:10]}")

    sample_size = 5000
    info_rng = np.random.default_rng(2027)
    sample = []; seen = set()
    while len(sample) < sample_size:
        T = tuple(sorted(info_rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)
    print(f"Info_set sample at L_2: {len(sample)}\n")

    K_dist = {}
    high_K = []
    extreme_K = -1; extreme_sup = None

    t0 = time.time()
    for idx, sup in enumerate(triples):
        coefs = [(idx*7 + 11) % (p-1) + 1, (idx*13 + 17) % (p-1) + 1, (idx*19 + 23) % (p-1) + 1]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        L1 = chain[1][0]
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)
        c_arr = np.array(fe_o, dtype=np.int64)
        d_arr = np.array(fo_o, dtype=np.int64)
        c_is_zero = (c_arr == 0).all()

        K = 0
        bad_alphas = []
        for alpha in range(p):
            h = (c_arr + alpha * d_arr) % p
            ext = batched_extras(info_arr, h, L2_arr, D2, inv_D2, p)
            d = n2 - k2 - int(ext.max())
            if d <= w_J_L2:
                K += 1
                bad_alphas.append(alpha)

        K_dist[K] = K_dist.get(K, 0) + 1
        if not c_is_zero and K > extreme_K:
            extreme_K = K
            extreme_sup = sup
        if K > 18 and not c_is_zero:
            high_K.append((sup, K, bad_alphas[:5]))

        if idx % 20 == 0:
            print(f"  [{idx+1}/{len(triples)}] non-deg max K = {extreme_K} (sup={extreme_sup})")

    print(f"\nTotal elapsed: {time.time()-t0:.0f}s")
    print(f"K distribution: {sorted(K_dist.items())}")
    print(f"Max non-degenerate K = {extreme_K} at sup={extreme_sup}")
    if high_K:
        print(f"\nHigh-K (> 18) supports:")
        for sup, K, alphas in high_K[:10]:
            print(f"  {sup}: K = {K}, sample bad α: {alphas}")
    else:
        print("\n** NO non-degenerate K > 18 — Conjecture E + Theorem 0187 prediction holds **")


if __name__ == "__main__":
    main()
