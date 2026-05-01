"""g3_split_d7_alphas.py — for the count=1153 witness, split the 16 d=7 alphas
by which support family they come from (even vs odd) and check each half is
a cyclotomic coset.

Structure: 2 unique error supports (even, odd) for f_e and f_o. For each
support, the codeword family parametrizes an affine line c_α = c_0 + α c_1.
For α to be "deeper" (d=7), one error position must vanish:
  α_i = - (f_e - c_0)[i] / (f_o - c_1)[i]   for i in support
giving up to 8 alphas per family.

Hypothesis: the 8 alphas in each family form a cyclotomic coset → 16 = 2 cosets.
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations

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


def find_closest_codeword_for_support(f_arr, L_arr, n, k, D, inv_D, p, target_support):
    """Find codeword c such that supp(f - c) = target_support (the complement is interpolation set)."""
    info_set = sorted(set(range(n)) - set(target_support))
    if len(info_set) < k:
        return None
    info_set = info_set[:n-len(target_support)]  # All non-error positions
    # We need ≥ k positions to interpolate. Use first k.
    T = info_set[:k]
    # Lagrange interpolate
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
        c_vals[i] = v
    # Verify f - c has support exactly target_support
    diff = (f_arr - c_vals) % p
    actual_support = tuple(i for i in range(n) if diff[i] != 0)
    return c_vals, diff, actual_support


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
    d7_alphas = [44, 147, 280, 327, 472, 484, 503, 528, 625, 650, 669, 681, 826, 873, 1006, 1109]

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2

    fhat = [0] * n0
    for ps, c in zip(pos, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    even_supp = (0, 2, 4, 6, 8, 10, 12, 14)
    odd_supp = (1, 3, 5, 7, 9, 11, 13, 15)

    print(f"=== Splitting d=7 alphas by support family ===\n")

    for label, supp in [('even', even_supp), ('odd', odd_supp)]:
        print(f"--- Family: support = {label} = {supp} ---")
        c_0_vals, e_e, supp_e = find_closest_codeword_for_support(f_e_arr, L1_arr, n1, k1, None, None, p, supp)
        c_1_vals, e_o, supp_o = find_closest_codeword_for_support(f_o_arr, L1_arr, n1, k1, None, None, p, supp)
        print(f"  e_e = f_e - c_0 = {e_e.tolist()}")
        print(f"  e_o = f_o - c_1 = {e_o.tolist()}")
        # For each i ∈ support with e_o[i] ≠ 0, alpha_i = -e_e[i]/e_o[i]
        family_alphas = []
        for i in supp:
            if e_o[i] != 0:
                alpha_i = (-int(e_e[i]) * pow(int(e_o[i]), p-2, p)) % p
                family_alphas.append((i, alpha_i))
        print(f"  Family alphas (8 expected):")
        for i, a in family_alphas:
            in_d7 = a in d7_alphas
            print(f"    α (zeros pos {i}) = {a}{'  *MATCHES d7*' if in_d7 else '  ?'}")
        family_alpha_set = set(a for _, a in family_alphas)
        in_d7_count = sum(1 for a in family_alpha_set if a in d7_alphas)
        print(f"  {len(family_alpha_set)} unique alphas, {in_d7_count} in d=7 set")

        coset = find_coset_structure(sorted(family_alpha_set), p)
        if coset:
            print(f"  CYCLOTOMIC COSET: {coset[0]} + {coset[1]}·μ_{coset[2]}")
            print(f"    H = {coset[3]}")
        else:
            print(f"  NOT a cyclotomic coset")
        print()


if __name__ == "__main__":
    main()
