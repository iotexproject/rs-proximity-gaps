"""probe_K2_exceptional_alphas.py — algebraic structure of E(f) for K=2 above-J.

For a K=2 above-J f with |E(f)| = m exceptional α_1's (i.e., d_1(α_1) ≤ δn_1 = 8),
extract those m α_1's and check:
  1. Do they satisfy any low-degree polynomial relation in F_p?
  2. Is the polynomial they're roots of related to a determinantal/resultant identity
     coming from the level-1 RS structure?
  3. Do they sit on a coset of a multiplicative or additive subgroup of F_p*?

Findings here would refine note 0130's framing: if E(f) is the root set of a
polynomial of degree ≤ d, we get |E(f)| ≤ d, giving an explicit algebraic bound.

Usage: python3 probe_K2_exceptional_alphas.py [n_cases=20] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from itertools import combinations as _combinations
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, parity_check, matvec, gauss_rank, even_odd_parts
from probe_K2_construct import construct_f_with_psi_in_U
from fast_tie_robust import fast_d1
from mds_decoder import precompute_diff_inv
from exact_above_J import is_above_J_early_exit


W_R = 3


def get_E_set(f, chain, p, threshold=8):
    """Return list of (α_1, d_1) ∈ F_p × Z with d_1(α_1) ≤ threshold."""
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_arr = np.array(list(_combinations(range(n1), k1)), dtype=np.int64)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    E = []
    for a1 in range(p):
        fold1_arr = (f_e_arr + a1 * f_o_arr) % p
        d = fast_d1(fold1_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1)
        if d <= threshold:
            E.append((a1, d))
    return E


def find_min_poly(roots, p, max_deg=20):
    """Find minimal polynomial of given roots in F_p[x]."""
    # Polynomial = ∏(x - r) — degree exactly len(roots).
    coeffs = [1]  # poly = 1
    for r in roots:
        # Multiply by (x - r): new[i] = old[i-1] - r * old[i]
        new = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new[i + 1] = (new[i + 1] + c) % p
            new[i] = (new[i] - r * c) % p
        coeffs = new
    return coeffs  # [a_0, a_1, ..., a_d]


def gen_K2_above_J_with_E(rng, p, chain, H_R, target_E_min=2):
    """Generate K=2 above-J f with |E(f)| ≥ target_E_min."""
    L0 = chain[0][0]
    n_R = N_R
    for _ in range(200):
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
        if T2 == T1: continue
        if len(set(T1) & set(T2)) > 1: continue

        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1: eps1[j] = rng.randrange(1, p)
        for j in T2: eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2: continue

        for _ in range(20):
            c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)
            above_J, _ = is_above_J_early_exit(f, L0, K0, W_J, p)
            if not above_J:
                continue
            E = get_E_set(f, chain, p, threshold=8)
            if len(E) >= target_E_min:
                ov = len(set(T1) & set(T2))
                return f, T1, T2, ov, E
    return None, None, None, None, None


def main():
    n_cases = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)

    print(f"K=2 exceptional α_1 algebraic-structure probe at p={p}")
    print(f"  Goal: find K=2 above-J cases with |E(f)| ≥ 2, examine their α_1 structure")
    print(f"  (E(f) = {{α_1 : d_1(α_1) ≤ δn_1 = 8}})")
    print()

    rng = random.Random(seed)
    cases_found = []
    n_attempts = 0
    t0 = time.time()
    while len(cases_found) < n_cases and n_attempts < n_cases * 4:
        n_attempts += 1
        f, T1, T2, ov, E = gen_K2_above_J_with_E(rng, p, chain, H_R, target_E_min=2)
        if f is None:
            continue
        cases_found.append((T1, T2, ov, E))
        alphas = [a for a, d in E]
        print(f"  [{len(cases_found)}/{n_cases}] T1={T1} T2={T2} ov={ov} |E|={len(E)} "
              f"α_1's: {alphas} (d_1's: {[d for a, d in E]})")

    print()
    print(f"  Found {len(cases_found)} cases in {n_attempts} attempts ({time.time()-t0:.0f}s)")
    print()

    print("=" * 75)
    print("ALGEBRAIC STRUCTURE ANALYSIS")
    print("=" * 75)

    for idx, (T1, T2, ov, E) in enumerate(cases_found):
        alphas = sorted(a for a, d in E)
        print()
        print(f"Case {idx+1}: T1={T1} T2={T2} ov={ov}")
        print(f"  α_1's (sorted): {alphas}")
        print(f"  d_1's: {[d for a, d in sorted(E)]}")

        # Analyze: is there a multiplicative subgroup structure?
        # F_97* has subgroups of orders dividing 96 = 2^5 * 3
        if 0 in alphas:
            nonzero = [a for a in alphas if a != 0]
        else:
            nonzero = alphas
        if len(nonzero) >= 2:
            # Check if nonzero α_1's lie in a coset of a subgroup
            # Compute pairwise ratios
            base = nonzero[0]
            ratios = [(a * pow(base, p - 2, p)) % p for a in nonzero]
            # Find order of the multiplicative group generated by ratios
            print(f"  Nonzero α_1 ratios from base={base}: {ratios}")
            # Check coset structure: if ratios lie in subgroup of order d
            for d in [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 96]:
                # Subgroup of order d in F_97* = {x : x^d = 1}
                in_subgroup = all(pow(r, d, p) == 1 for r in ratios)
                if in_subgroup:
                    print(f"    ★ ratios lie in subgroup of order {d} of F_{p}*")
                    break

        # Compute minimal polynomial
        coeffs = find_min_poly(alphas, p)
        deg = len(coeffs) - 1
        # Show it normalized (leading coef 1)
        print(f"  Minimal polynomial of E(f) over F_{p} (deg {deg}):")
        print(f"    coeffs (low to high): {coeffs}")
        # Check if this poly factors nicely (e.g., x^d - c)
        if deg >= 2:
            # Test x^d - c form
            nz_count = sum(1 for c in coeffs[1:-1] if c != 0)
            if nz_count == 0 and coeffs[0] != 0:
                print(f"    ★★ POLY HAS FORM x^{deg} + c (only top + const), suggests subgroup coset!")

    print()
    print("=" * 75)
    print("INTERPRETATION")
    print("=" * 75)
    print()
    print(f"  If E(f) = roots of polynomial of degree d ≤ small constant,")
    print(f"  this gives |E(f)| ≤ d, providing a Bezout-style bound.")
    print()
    print(f"  Multiplicative-subgroup structure (ratios in subgroup of small order)")
    print(f"  would suggest the resultant cuts out a coset, generalizing the K=1")
    print(f"  (i, i+8) algebraic family (note 0123).")


if __name__ == '__main__':
    main()
