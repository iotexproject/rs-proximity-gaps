"""g3_analyze_count1153.py — analyze the structure of the count=q=1153 witness.

Witness: pos=(19,20,23), coeffs=(153,252,208) at q=1153, n_0=32, k_0=8.
- dist(f, RS_8 on L_0) = 21
- dist(f_e, RS_4 on L_1) = 8
- dist(f_o, RS_4 on L_1) = 8
- 16 alphas at d_1=7, 1137 alphas at d_1=8 (out of 1153 total).

Key questions:
1. Are the 16 d=7 alphas a cyclotomic coset (Conjecture D-light)?
2. Are c_0 = closest_codeword(f_e), c_1 = closest_codeword(f_o), and do they
   share the same "error support" S (size 8) explaining count=q?
3. Find c_0, c_1 explicitly, identify support S, check structural symmetry.
4. Is f's coefficient pattern (153, 252, 208) generic or special?
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def find_closest_codewords(f_arr, L_arr, n, k, D, inv_D, p, target_dist):
    """Find ALL codewords at distance ≤ target_dist from f. Returns list of (c_vals, support_of_error)."""
    info_sets = list(combinations(range(n), k))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    extras = batched_extras(info_sets_arr, f_arr, L_arr, D, inv_D, p)
    threshold_extras = n - k - target_dist
    good = np.where(extras >= threshold_extras)[0]
    out = []
    for idx in good:
        T = info_sets_arr[idx]
        # Reconstruct codeword by interpolation
        # c(L[i]) for i ∈ [n], using Lagrange through (L[T[j]], f[T[j]])
        c_vals = np.zeros(n, dtype=np.int64)
        for i in range(n):
            v = 0
            for j_idx in range(k):
                Lj = L_arr[T[j_idx]]
                Li = L_arr[i]
                if Li == Lj:
                    v = f_arr[T[j_idx]]
                    break
                num = 1
                den = 1
                for s in range(k):
                    if s == j_idx: continue
                    num = (num * (Li - L_arr[T[s]])) % p
                    den = (den * (Lj - L_arr[T[s]])) % p
                den_inv = pow(int(den), p - 2, p)
                v = (v + f_arr[T[j_idx]] * num * den_inv) % p
            else:
                pass
            c_vals[i] = v
        diff = (f_arr - c_vals) % p
        supp = tuple(np.where(diff != 0)[0])
        out.append((tuple(c_vals.tolist()), supp))
    return out


def is_subgroup(S, p):
    Sset = set(S)
    for a in S:
        for b in S:
            if (a * b) % p not in Sset:
                return False
    return True


def find_coset_structure(bad, p):
    if len(bad) == 0:
        return None
    bad = sorted(bad)
    for beta in range(p):
        translates = sorted([(b - beta) % p for b in bad])
        if 0 in translates:
            continue
        first = translates[0]
        first_inv = pow(first, p - 2, p)
        ratios = sorted({(t * first_inv) % p for t in translates})
        if is_subgroup(ratios, p):
            return (beta, first, len(ratios), ratios)
    return None


def main():
    p = 1153
    n0, k0 = 32, 8
    pos = (19, 20, 23)
    coeffs = (153, 252, 208)

    print(f"=== Analyzing witness: q={p}, pos={pos}, coeffs={coeffs} ===\n")

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    fhat = [0] * n0
    for ps, c in zip(pos, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    print(f"L_1 = {L1}")
    print(f"f_e on L_1: {f_e}")
    print(f"f_o on L_1: {f_o}")

    # --- Question 1: 16 d=7 alphas — cyclotomic? ---
    print(f"\n--- Q1: Find d=7 alphas and check structure ---")
    threshold_d7 = 7
    bad7 = []
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 == threshold_d7:
            bad7.append(a)
    print(f"  d=7 alphas ({len(bad7)}): {bad7[:50]}{'...' if len(bad7) > 50 else ''}")
    coset = find_coset_structure(bad7, p)
    if coset is not None:
        beta, lam, h_ord, H = coset
        print(f"  COSET STRUCTURE: bad7 = {beta} + {lam}·μ_{h_ord}, |H|={h_ord}")
        print(f"  H = {H}")
    else:
        print(f"  No coset structure for d=7 alphas")

    # --- Question 2/3: closest codewords for f_e, f_o ---
    print(f"\n--- Q2: Find closest RS_4 codewords to f_e and f_o (dist=8) ---")
    cwds_e = find_closest_codewords(f_e_arr, L1_arr, n1, k1, D1, inv_D1, p, 8)
    cwds_o = find_closest_codewords(f_o_arr, L1_arr, n1, k1, D1, inv_D1, p, 8)
    print(f"  # codewords at d≤8 from f_e: {len(cwds_e)}")
    print(f"  # codewords at d≤8 from f_o: {len(cwds_o)}")

    # Get unique error supports
    supps_e = sorted(set(s for _, s in cwds_e))
    supps_o = sorted(set(s for _, s in cwds_o))
    print(f"  # unique error supports for f_e: {len(supps_e)}")
    print(f"  # unique error supports for f_o: {len(supps_o)}")

    # Check overlaps
    common_supps = set(supps_e) & set(supps_o)
    print(f"  # COMMON supports (key for count=q!): {len(common_supps)}")
    if common_supps:
        for s in sorted(common_supps)[:5]:
            print(f"    common support (size {len(s)}): {s}")

    # --- Question: support of f_o-c_1 vs f_e-c_0 ---
    print(f"\n--- Q3: Show explicit (c_0, c_1) with shared support ---")
    if common_supps:
        common = sorted(common_supps)[0]
        print(f"  Using common support S = {common}")
        # Find a codeword c_0 with f_e - c_0 supported in this S
        c_0_vals, _ = next((c, s) for c, s in cwds_e if s == common)
        c_1_vals, _ = next((c, s) for c, s in cwds_o if s == common)
        print(f"  c_0 (closest to f_e):")
        print(f"    f_e - c_0 = {[(f_e[i] - c_0_vals[i]) % p for i in range(n1)]}")
        print(f"  c_1 (closest to f_o):")
        print(f"    f_o - c_1 = {[(f_o[i] - c_1_vals[i]) % p for i in range(n1)]}")
        # Verify the union argument: for ANY α, fold_α - (c_0 + α c_1) is supported in S
        print(f"\n  Triangle check: for α=1, supp(fold_α - (c_0 + α c_1)):")
        a = 1
        fold_alpha = [(f_e[i] + a * f_o[i]) % p for i in range(n1)]
        c_alpha = [(c_0_vals[i] + a * c_1_vals[i]) % p for i in range(n1)]
        diff = [(fold_alpha[i] - c_alpha[i]) % p for i in range(n1)]
        nonzero_supp = tuple(i for i in range(n1) if diff[i] != 0)
        print(f"    supp(fold_α - c_α) = {nonzero_supp}, size {len(nonzero_supp)}")
        print(f"    common S = {common}, size {len(common)}")
        print(f"    supp ⊆ S? {set(nonzero_supp).issubset(common)}")

    # --- Question 4: is the coefficient pattern special? ---
    print(f"\n--- Q4: coefficient ratios ---")
    print(f"  c_19 = {coeffs[0]}, c_20 = {coeffs[1]}, c_23 = {coeffs[2]}")
    print(f"  c_19/c_20 = {(coeffs[0] * pow(coeffs[1], p-2, p)) % p}")
    print(f"  c_23/c_20 = {(coeffs[2] * pow(coeffs[1], p-2, p)) % p}")
    print(f"  c_19/c_23 = {(coeffs[0] * pow(coeffs[2], p-2, p)) % p}")
    print(f"  c_19·c_23 mod {p} = {(coeffs[0] * coeffs[2]) % p}")
    # Check if -c_19/c_23 is in μ_8 (square in μ_16)
    ratio = (- coeffs[0] * pow(coeffs[2], p-2, p)) % p
    in_mu8 = pow(ratio, 8, p) == 1
    in_mu16 = pow(ratio, 16, p) == 1
    print(f"  -c_19/c_23 = {ratio}; (·)^8 = {pow(ratio, 8, p)} (in μ_8? {in_mu8})")
    print(f"                          (·)^16 = {pow(ratio, 16, p)} (in μ_16? {in_mu16})")


if __name__ == "__main__":
    main()
