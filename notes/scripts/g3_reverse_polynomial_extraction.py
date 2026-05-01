"""g3_reverse_polynomial_extraction.py — extract the degree-9 polynomial
whose roots are the bad α_1's in Reverse Pattern.

For (15, 18, 19) at (32, 8), we have h(α_1) = c·z^4 + α_1·v(z) on L_2 of
order 8 with z^4 = ±1 (sign character).

Bad α_1: dist(h(α_1), RS_2(L_2)) ≤ 4 = w_J. Empirically 9 such α_1 across
all coef trials.

We compute P(α_1) = ∏_{β bad} (α_1 - β), factor over F_p, and look for
trinomial / power-of-prime structure (Bluher signature).
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain, even_odd_parts, modinv


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def poly_mul(a, b, p):
    """Multiply two polynomials mod p. Coefficients ascending."""
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if not ai: continue
        for j, bj in enumerate(b):
            if not bj: continue
            out[i+j] = (out[i+j] + ai*bj) % p
    return out


def poly_from_roots(roots, p):
    """Compute monic polynomial with given roots."""
    poly = [1]
    for r in roots:
        # multiply by (x - r)
        poly = poly_mul(poly, [(-r) % p, 1], p)
    return poly


def poly_show(poly, p):
    """Show polynomial nicely."""
    terms = []
    for i, c in enumerate(poly):
        if c == 0: continue
        c_disp = c if c <= p//2 else c - p
        if i == 0:
            terms.append(f"{c_disp}")
        elif i == 1:
            terms.append(f"{c_disp}·x")
        else:
            terms.append(f"{c_disp}·x^{i}")
    return " + ".join(terms[::-1]) if terms else "0"


def find_bad_alpha1(fe_o, fo_o, n2, p, w_J, L2_arr):
    """Find α_1 where h(α_1) = fe_o + α_1·fo_o is bad on L_2 = RS_2.

    bad means dist ≤ w_J. For RS_2 on L_2 of order 8: codewords are
    affine a_0 + a_1·z. dist(h, RS_2) = min over (a_0, a_1) of #{z: h(z) ≠ a_0 + a_1·z}.
    Equivalent to max over (a_0, a_1) of #agreements.
    """
    bad_a1 = []
    for a1 in range(p):
        h = [(int(fe_o[i]) + a1 * int(fo_o[i])) % p for i in range(n2)]
        # For each pair (i, j) with i<j: fit affine, count agreements
        max_agree = 0
        for i in range(n2):
            for j in range(i+1, n2):
                yi, yj = int(L2_arr[i]), int(L2_arr[j])
                denom = (yi - yj) % p
                if denom == 0: continue
                a1_lin = ((h[i] - h[j]) * modinv(denom, p)) % p
                a0_lin = (h[i] - a1_lin * yi) % p
                agree = sum(1 for k in range(n2)
                           if (a0_lin + a1_lin * int(L2_arr[k])) % p == h[k])
                if agree > max_agree: max_agree = agree
                if max_agree >= n2 - w_J:
                    break  # bad confirmed
            if max_agree >= n2 - w_J:
                break
        # also check constant codewords (a_1 = 0)
        for a0 in range(p):
            agree = sum(1 for k in range(n2) if h[k] == a0)
            if agree > max_agree: max_agree = agree
        if (n2 - max_agree) <= w_J:
            bad_a1.append(a1)
    return bad_a1


def main():
    p = 97
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L2 = 4

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)

    sup = (15, 18, 19)
    print(f"=== Polynomial extraction: support {sup} at (32,8), q={p} ===\n")

    poly_collection = []

    for trial in range(5):
        random.seed(2026 + trial)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)

        # bad α_1 set
        bad_a1 = find_bad_alpha1(fe_o, fo_o, n2, p, w_J_L2, L2_arr)

        print(f"--- Trial {trial}, coefs={coefs} ---")
        print(f"  Bad α_1 ({len(bad_a1)}): {bad_a1}")

        # Construct polynomial
        if len(bad_a1) == 9:
            P = poly_from_roots(bad_a1, p)
            print(f"  Coefs ascending: {P}")
            print(f"  P(x) = {poly_show(P, p)}")

            # Test for sparsity (trinomial?)
            nonzero = [(i, P[i]) for i in range(len(P)) if P[i] != 0]
            print(f"  Number of nonzero coefs: {len(nonzero)}")
            print(f"  Nonzero positions: {[i for i, _ in nonzero]}")

            # Check x^9 - x form (i.e., F_q^* like)
            # Or x^9 - cx form
            # Or x^9 + ax + b form (Bluher)

            # Check if P / x has factor x^8 - 1 etc.
            # First reduce mod x^9 - 1?
            poly_collection.append((coefs, bad_a1, P, fe_o, fo_o))
        else:
            print(f"  WARNING: not 9 bad α_1's")
        print()

    # Now look for INVARIANT structure across trials
    print("=== Cross-trial structure ===")
    if len(poly_collection) >= 2:
        # Hypothesis: the bad α_1 set is closed under α_1 → -α_1?
        for coefs, bad_a1, P, fe_o, fo_o in poly_collection[:3]:
            negated = sorted([(p - a) % p for a in bad_a1])
            print(f"  coefs={coefs}: bad_a1 = {sorted(bad_a1)}")
            print(f"                -bad_a1 = {negated}")
            print(f"                closed under negation? {sorted(bad_a1) == negated}")

        # Hypothesis: rescaling — if bad_a1[1]/bad_a1[2] in different trials...
        # Hypothesis: bad_a1 includes α_1 = 0 (trivial)?
        for coefs, bad_a1, P, _, _ in poly_collection[:3]:
            print(f"  coefs={coefs}: 0 ∈ bad? {0 in bad_a1}")

    # Compute polynomial in normalized form: substitute α_1 → c_o · t / c_e where
    # c_o is the coefficient of fo_o's leading term, etc.
    # This should reveal the universal Bluher-shape
    print("\n=== Normalized polynomial test ===")
    if len(poly_collection) >= 1:
        # For trial 0: (f_e)_o = 41, 56 alternating = 41·z^4 (since 41+56=97)
        # Wait — need to express (f_e)_o as a single-monomial.
        coefs, bad_a1, P, fe_o, fo_o = poly_collection[0]
        # (f_e)_o = c_e + (something)·z^?... Let's identify
        # On L_2, (f_e)_o = c·z^4 since z^4 = ±1, and we see [c, -c, c, -c, ...]
        c_4 = int(fe_o[0])  # value at z=1, which is c·1 = c
        print(f"  Trial 0: c_4 = {c_4}, (f_e)_o = {[int(x) for x in fe_o]}")
        print(f"  Verify: c_4 · z^4: {[(c_4 * pow(int(z), 4, p)) % p for z in L2_arr]}")

        # (f_o)_o on L_2 — express via DFT
        # On L_2 of order 8, (f_o)_o = sum of c_j · z^{j mod 8} for j ∈ supp ∩ "odd-odd indices"
        # supp = (15, 18, 19); odd-odd = j ≡ 3 mod 4 — that's 15 and 19.
        # 15 mod 8 = 7, 19 mod 8 = 3. So (f_o)_o = c_15·z^7 + c_19·z^3.
        # In our DFT convention (Σ f̂_j ω^{ij}), but the splitting fold/even-odd
        # convention should result in this.
        # Actually fo_o on L_2 (length 8) should equal:
        # c_15·z^7 + c_19·z^3 where z ranges over L_2 = ⟨ω^4⟩ of order 8
        # But only modulo a normalization factor (1/(2·2) = 1/4 typically).
        # Let's verify:
        c_15, c_19 = coefs[0], coefs[2]
        for z_idx in range(n2):
            z = int(L2_arr[z_idx])
            val_th = (c_15 * pow(z, 7, p) + c_19 * pow(z, 3, p)) % p
            val_th_quart = (val_th * modinv(4, p)) % p
            print(f"    z={z}: theoretical (with 1/4): {val_th_quart}, actual: {int(fo_o[z_idx])}")


if __name__ == "__main__":
    main()
