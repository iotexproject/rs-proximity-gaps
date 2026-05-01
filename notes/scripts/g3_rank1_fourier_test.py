"""g3_rank1_fourier_test.py — apply PR #373's rank-1 Fourier residue projection
test to count > 0 supports at q=1153, (32, 8).

For curated count > 0 supports:
  1. compute bad-alpha set B(f) directly using batched_extras (full enumeration
     of C(16, 4) = 1820 info sets at L_1 — feasible)
  2. compute smallest H ≤ F_q* such that B(f) is union of H-cosets
  3. report H, # cosets, coset structure
"""
import sys, os, math, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft_local(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def find_primroot(q):
    n = q - 1
    factors = set()
    m = n
    d = 2
    while d * d <= m:
        if m % d == 0:
            factors.add(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        factors.add(m)
    for g in range(2, q):
        if all(pow(g, n // f, q) != 1 for f in factors):
            return g
    return None


def find_subgroup_closure(B, q, g_prim, divisors):
    """Smallest H ≤ F_q* (with |H| dividing q-1) such that B is union of
    H-cosets.  Returns (|H|, generator)."""
    if not B:
        return None, None
    B_set = frozenset(B)
    for h in divisors:  # ascending
        h_gen = pow(g_prim, (q - 1) // h, q)
        # generate H
        H = [1]
        x = 1
        for _ in range(h - 1):
            x = x * h_gen % q
            H.append(x)
        ok = True
        for b in B_set:
            for u in H:
                if (b * u) % q not in B_set:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return h, h_gen
    return q - 1, g_prim


def divisors_sorted(n):
    out = []
    for d in range(1, n + 1):
        if n % d == 0:
            out.append(d)
    return out


def compute_bad_alpha(positions, coeffs, p, n0, k0, threshold):
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1 = len(L1)
    k1 = k0 // 2

    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    bad = []
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            bad.append(alpha)
    return bad, f_e, f_o, L1


def coset_decomposition(B, h, h_gen, q):
    """Decompose B (subset of F_q*) into cosets of subgroup of order h."""
    H = set([1])
    x = 1
    for _ in range(h - 1):
        x = x * h_gen % q
        H.add(x)
    cosets = []
    rem = set(B)
    while rem:
        seed = min(rem)
        co = frozenset((seed * u) % q for u in H)
        if not co.issubset(rem):
            return None  # shouldn't happen if H closure verified
        cosets.append((seed, co))
        rem -= co
    return cosets


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))  # = 8

    g_prim = find_primroot(p)
    divisors = divisors_sorted(p - 1)
    print(f"q = {p}, primitive root = {g_prim}")
    print(f"|F_q*| = {p-1} = product of: {[d for d in divisors if d != 1 and d != p-1][:10]}...")
    print(f"divisors of {p-1}: {divisors}")

    # curated count > 0 supports (sample)
    samples = {
        9: [(8, 9, 20), (12, 13, 17), (14, 15, 19)],  # count=9
        8: [(8, 20, 21), (12, 16, 17)],
        6: [(8, 16, 25), (10, 18, 27)],
        5: [(8, 9, 16), (10, 11, 18)],
        4: [(8, 17, 24), (10, 19, 26), (8, 9, 24), (8, 16, 17)],
    }

    print(f"=== rank-1 Fourier / multiplicative-coset test at q={p}, ({n0},{k0}) ===\n")

    t_start = time.time()
    for cnt_pred, sup_list in sorted(samples.items(), reverse=True):
        for sup in sup_list:
            t0 = time.time()
            coeffs = (1,) * len(sup)
            bad, f_e, f_o, L1 = compute_bad_alpha(sup, coeffs, p, n0, k0, threshold)
            elapsed = time.time() - t0

            print(f"--- support = {sup} (predicted count = {cnt_pred}, actual = {len(bad)}) [{elapsed:.0f}s] ---")
            print(f"  bad alphas: {bad if len(bad) <= 20 else f'[{bad[:8]}...{bad[-4:]}]'}")

            B_nz = [a for a in bad if a != 0]
            if B_nz:
                h, h_gen = find_subgroup_closure(B_nz, p, g_prim, divisors)
                cosets = coset_decomposition(B_nz, h, h_gen, p)
                print(f"  smallest H closing B (excl 0): |H|={h}, gen={h_gen}, # cosets={len(cosets) if cosets else '?'}")
                if cosets and len(cosets) <= 6:
                    for seed, co in cosets:
                        co_sorted = sorted(co)
                        print(f"    coset seed={seed}: |co|={len(co)}, first={co_sorted[:6]}")
            else:
                print(f"  bad ⊂ {{0}}: no nonzero α")

            # also test L_1-rotation symmetry on the witness sets
            # (skipped for time — implement if needed)
            print()

    print(f"=== total time {time.time()-t_start:.0f}s ===")


if __name__ == "__main__":
    main()
