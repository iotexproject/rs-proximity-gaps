"""probe_E7_alphas.py — extract the 7 exceptional α_1's of the K=2 (18,8) ov=1 case
and check their algebraic structure.

This is the worst-case |E(f)|=7 from audit_tie_robust_K2 (seed=4242, breach (18,8)).
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank, even_odd_parts
from probe_K2_construct import construct_f_with_psi_in_U
from fast_tie_robust import fast_d1
from mds_decoder import precompute_diff_inv

W_R = 3


def reproduce_breach_18_8(p, chain, H_R, seed=4242):
    """Reconstruct the (pair_idx=18, f_idx=8) breach from audit_tie_robust_K2."""
    rng = random.Random(seed)
    L0 = chain[0][0]
    n_R = N_R
    w_R = W_R
    target = (18, 8)
    for pair_idx in range(30):
        T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            available = [j for j in range(n_R) if j not in T1]
            if len(available) < w_R:
                continue
            T2 = tuple(sorted(rng.sample(available, w_R)))
        else:
            shared = rng.choice(list(T1))
            others_pool = [j for j in range(n_R) if j not in T1]
            if len(others_pool) < w_R - 1:
                continue
            others = rng.sample(others_pool, w_R - 1)
            T2 = tuple(sorted([shared] + others))
        if T2 == T1 or len(set(T1) & set(T2)) > 1:
            continue
        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1:
            eps1[j] = rng.randrange(1, p)
        for j in T2:
            eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2:
            continue
        for f_idx in range(10):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            if (pair_idx, f_idx) == target:
                return f, T1, T2, fhat
    return None, None, None, None


def find_min_poly(roots, p):
    coeffs = [1]
    for r in roots:
        new = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new[i + 1] = (new[i + 1] + c) % p
            new[i] = (new[i] - r * c) % p
        coeffs = new
    return coeffs


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    print(f"Probing E(f) algebraic structure for K=2 (18,8) ov=1 breach (|E|=7 case)")
    print()

    f, T1, T2, fhat = reproduce_breach_18_8(p, chain, H_R)
    if f is None:
        print("  ERROR: failed to reproduce breach (18,8). Check seed/iteration logic.")
        return
    print(f"  Reconstructed: T1={T1} T2={T2}, ov={len(set(T1)&set(T2))}")
    print(f"  Fourier support of f: {[i for i,v in enumerate(fhat) if v != 0]}")
    print()

    # Compute E(f)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    E = []
    d_dist = {}
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        d_dist[d] = d_dist.get(d, 0) + 1
        if d <= 8:
            E.append((a1, d))

    print(f"  d_1 distribution across α_1 ∈ F_{p}: {sorted(d_dist.items())}")
    print(f"  |E(f)| = {len(E)}")
    print(f"  Exceptional (α_1, d_1): {E}")
    print()

    if len(E) == 0:
        print("  No exceptional α_1 — nothing to analyze.")
        return

    alphas = sorted(a for a, d in E)
    print(f"  α_1's sorted: {alphas}")

    # ALGEBRAIC STRUCTURE TESTS

    print()
    print("=" * 75)
    print("Test 1: Multiplicative-subgroup coset structure")
    print("=" * 75)
    nonzero = [a for a in alphas if a != 0]
    if len(nonzero) >= 2:
        base = nonzero[0]
        ratios = [(a * pow(base, p - 2, p)) % p for a in nonzero]
        print(f"  Nonzero α_1's: {nonzero}")
        print(f"  Ratios from base={base}: {sorted(set(ratios))}")
        # F_97* has order 96; subgroups of order d for d | 96
        for d in [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 96]:
            in_subgroup = all(pow(r, d, p) == 1 for r in ratios)
            if in_subgroup:
                print(f"  ★ Ratios ⊆ multiplicative subgroup of order {d}")
                break
        else:
            print(f"  No multiplicative-subgroup containment found.")

    print()
    print("=" * 75)
    print("Test 2: Additive structure (linear pattern)")
    print("=" * 75)
    if len(alphas) >= 3:
        diffs = sorted(set((alphas[i+1] - alphas[i]) % p for i in range(len(alphas) - 1)))
        print(f"  Consecutive diffs (mod p): {diffs}")
        if len(diffs) == 1:
            print(f"  ★ ARITHMETIC PROGRESSION (common diff {diffs[0]})")

    print()
    print("=" * 75)
    print("Test 3: Minimal polynomial of E(f) in F_p[x]")
    print("=" * 75)
    coeffs = find_min_poly(alphas, p)
    deg = len(coeffs) - 1
    print(f"  Min poly degree (= |E(f)|): {deg}")
    # Print poly nicely
    terms = []
    for i, c in enumerate(coeffs):
        if c != 0:
            if i == 0:
                terms.append(str(c))
            elif i == 1:
                terms.append(f"{c}·x" if c != 1 else "x")
            else:
                terms.append(f"{c}·x^{i}" if c != 1 else f"x^{i}")
    print(f"  Min poly: {' + '.join(terms[::-1])}")
    nonzero_mid = sum(1 for c in coeffs[1:-1] if c != 0)
    if nonzero_mid == 0 and coeffs[0] != 0:
        # Form x^deg + c
        print(f"  ★★ POLY HAS FORM x^{deg} - c (only top + const)")
        print(f"     Roots are {deg}-th roots of {(-coeffs[0]) % p} in F_{p}")

    print()
    print("=" * 75)
    print("Test 4: Are the α_1's roots of a low-degree polynomial in some auxiliary ring?")
    print("=" * 75)
    # Check: for each α_1 ∈ E, what is the d_1 codeword? Is there structure in
    # the codewords?
    print(f"  (For now, just summarize d_1 values: {[d for a,d in E]})")
    print(f"  Mean d_1: {sum(d for a,d in E) / len(E):.2f}")

    print()
    print("=" * 75)
    print("Test 5: Norm of α_1's (sum, product, sym fns)")
    print("=" * 75)
    s = sum(alphas) % p
    pr = 1
    for a in alphas:
        pr = (pr * a) % p
    print(f"  sum α_1 = {s} mod {p}")
    print(f"  prod α_1 = {pr} mod {p}")


if __name__ == '__main__':
    main()
