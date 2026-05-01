"""g3_K_256_64_orbit_test.py — test Theorem 0187 prediction at (256, 64).

For Reverse Pattern at (256, 64), find a saturating support with pencil
(a, b) on L_2 (order 64) such that gcd(b-a, 64) = 4 → orbit size = 16.

Predicted K = 1 + 16 + 1 = 18 (with the +1 saturating column).

Compare to Note 0184 finding K = 1 (likely undersample).

Approach: take small set of supports, pick the one with saturating
pencil, run with large enough sample to detect all orbit elements.
"""
import sys, os, random, time
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
    p = 257
    n0, k0 = 256, 64
    n1, k1 = 128, 32
    n2, k2 = 64, 16
    w_J_L2 = n2 - int(round(np.sqrt(k2 * n2)))  # = 32

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    # Reverse pattern: support positions ≡ 2 or 3 mod 4
    # Try a few well-spaced 3-pos supports
    test_supports = [
        (87 + 128, 102 + 128, 103 + 128),  # (215, 230, 231) mirror of (87,102,103)+128
        (171, 174, 175),
        (175, 198, 203),
        (87, 90, 91),
        (139, 154, 155),  # (87, 102, 103) - 64 + 116 — random Reverse
    ]
    # Filter to mod 4 ∈ {2, 3}
    test_supports = [
        sup for sup in test_supports
        if all(j % 4 in (2, 3) for j in sup) and all(j < n0 for j in sup)
    ]
    print(f"Testing supports: {test_supports}")

    # Use larger sample for (256, 64) — n_2 = 64
    sample_size = 50000
    rng = np.random.default_rng(2026)
    sample = []; seen = set()
    while len(sample) < sample_size:
        T = tuple(sorted(rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)
    print(f"Sample size at L_2: {len(sample)} of C(64,16) = 488T (~10^-10)")

    for sup in test_supports:
        random.seed(2026 + hash(sup) % 1000)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)

        # For Reverse Pattern: a = b = 0, so c = (f_e)_o, d = (f_o)_o.
        # h(α_1) = c + α_1·d on L_2.
        c_arr = np.array(fe_o, dtype=np.int64)
        d_arr = np.array(fo_o, dtype=np.int64)

        print(f"\n=== sup={sup}, coefs={coefs} ===")
        # Find DFT positions of c, d on L_2
        from g3_pencil_count_table import find_subgroup
        # ... actually use evaluate_dft approach: c_arr = c values on L_2
        # Find DFT support by inverse DFT
        n_inv = pow(n2, p-2, p)
        c_dft = []; d_dft = []
        for k in range(n2):
            cv, dv = 0, 0
            for i, z in enumerate(L2):
                w = pow(int(z), -k, p)
                cv = (cv + int(c_arr[i]) * w) % p
                dv = (dv + int(d_arr[i]) * w) % p
            c_dft.append(cv * n_inv % p)
            d_dft.append(dv * n_inv % p)
        c_supp = [(j, v) for j, v in enumerate(c_dft) if v != 0]
        d_supp = [(j, v) for j, v in enumerate(d_dft) if v != 0]
        print(f"  c DFT supp on L_2: {c_supp}")
        print(f"  d DFT supp on L_2: {d_supp}")

        # Bad α count: enumerate all α
        bad_alphas = []
        for alpha in range(p):
            h = (c_arr + alpha * d_arr) % p
            ext = batched_extras(info_arr, h, L2_arr, D2, inv_D2, p)
            d = n2 - k2 - int(ext.max())
            if d <= w_J_L2:
                bad_alphas.append((alpha, d))
        print(f"  N (sampled) = {len(bad_alphas)}")
        if bad_alphas:
            sample_alphas = bad_alphas[:8]
            print(f"  Sample bad α: {[a for a, _ in sample_alphas]}")
            dists = sorted(set(d for _, d in bad_alphas))
            print(f"  Distinct dists: {dists}")


if __name__ == "__main__":
    main()
