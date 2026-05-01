"""g3_reverse_factor_polys.py — factor polynomials whose roots are bad α_1's,
look for shared factors / structure across trials.

Hypothesis: P(α_1) is a degree-9 polynomial that factors as (low-degree
factors) × (Bluher-shape factor). Or it's a deformation of a fixed form.
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


def poly_eval(P, x, p):
    return sum(c * pow(x, i, p) for i, c in enumerate(P)) % p


def poly_normalize(P, p):
    # Normalize: monic, then divide by x^k where k is order of vanishing at 0
    while P and P[0] == 0:
        P = P[1:]
    if not P: return [0]
    inv_lead = modinv(P[-1], p)
    return [(c * inv_lead) % p for c in P]


def poly_reduce(num, den, p):
    """num / den over F_p[x], return quotient if exact."""
    num = list(num); den = list(den)
    while num and num[-1] == 0: num.pop()
    while den and den[-1] == 0: den.pop()
    if not den: raise ValueError("zero den")
    inv_lead_den = modinv(den[-1], p)
    quot = []
    for _ in range(len(num) - len(den) + 1):
        if not num or len(num) < len(den):
            quot.append(0)
            continue
        c = (num[-1] * inv_lead_den) % p
        quot.append(c)
        for i in range(len(den)):
            idx = len(num) - len(den) + i
            num[idx] = (num[idx] - c * den[i]) % p
        num.pop()
    return quot[::-1], num  # quotient, remainder


def poly_gcd(a, b, p):
    a = list(a); b = list(b)
    while b and b[-1] == 0: b.pop()
    while a and a[-1] == 0: a.pop()
    while b:
        _, rem = poly_reduce(a, b, p)
        a, b = b, rem
        while b and b[-1] == 0: b.pop()
    return a


def poly_mul(a, b, p):
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if not ai: continue
        for j, bj in enumerate(b):
            if not bj: continue
            out[i+j] = (out[i+j] + ai*bj) % p
    return out


def poly_from_roots(roots, p):
    poly = [1]
    for r in roots:
        poly = poly_mul(poly, [(-r) % p, 1], p)
    return poly


def find_bad_alpha1(fe_o, fo_o, n2, p, w_J, L2_arr):
    bad_a1 = []
    for a1 in range(p):
        h = [(int(fe_o[i]) + a1 * int(fo_o[i])) % p for i in range(n2)]
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
                if max_agree >= n2 - w_J: break
            if max_agree >= n2 - w_J: break
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
    print(f"=== Polynomial factoring: {sup} at q={p} ===\n")

    polys = []
    for trial in range(8):
        random.seed(2026 + trial)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)

        bad_a1 = find_bad_alpha1(fe_o, fo_o, n2, p, w_J_L2, L2_arr)
        P = poly_from_roots(bad_a1, p)
        polys.append((trial, coefs, bad_a1, P, fe_o, fo_o))

        print(f"Trial {trial}: coefs={coefs}, |bad|={len(bad_a1)}")
        print(f"  bad: {bad_a1}")
        print(f"  P: {P}")

    print("\n=== Brute-force factoring (trial linear factors) ===")
    for trial, coefs, bad_a1, P, fe_o, fo_o in polys[:3]:
        print(f"\nTrial {trial}: bad = {bad_a1}")
        # Already factored as ∏(x - β). Check for irreducible factors of degree > 1?
        # Test: x^96 - x ≡ 0 mod P (Fermat's little theorem; if all roots in F_p, then P | x^96-x, automatic)
        # Test for higher degree factors: P_irreducible_test
        # Direct: check if (x^p - x) % P(x) = 0
        # Compute x^p mod P
        # Simpler: just check degrees of factors via Cantor-Zassenhaus? Skip; we already
        # KNOW P factors fully into linear (since we constructed it from roots).

        # The interesting structure: do these bad_a1 lie on a curve / variety?
        # Test: linear-fractional invariance
        # For trial 0: bad = [0, 5, 8, 23, 31, 32, 68, 86, 88]
        # 86 = -11, 88 = -9, 68 = -29, 32 = 32, 31 = 31, 23 = 23, 8 = 8, 5 = 5, 0 = 0
        as_signed = [(b if b <= p//2 else b - p) for b in bad_a1]
        print(f"  signed: {as_signed}")
        # Test: pairs summing to specific values
        sums = sorted(set((a + b) % p for a in bad_a1 for b in bad_a1 if a != b))
        most_common_sum = max(set(sums), key=lambda s: sum(1 for a in bad_a1 for b in bad_a1
                                                          if a != b and (a+b) % p == s))
        cnt = sum(1 for a in bad_a1 for b in bad_a1 if a != b and (a+b) % p == most_common_sum)
        print(f"  most common pair-sum: {most_common_sum} (signed {most_common_sum if most_common_sum <= p//2 else most_common_sum-p}), count={cnt}")
        # Look for structure α + β = constant (additive symmetry)
        for s_test in range(p):
            paired = []
            used = set()
            for a in bad_a1:
                if a in used: continue
                b = (s_test - a) % p
                if b in bad_a1 and b != a:
                    paired.append((a, b))
                    used.add(a); used.add(b)
            if len(paired) >= 3:
                print(f"  α + β = {s_test} pairs: {paired}")

    print("\n=== Looking for invariants in the polynomial coefs ===")
    # Look for ratios / patterns in P[i] across trials
    # First: signed coefficients
    print("Signed coefs (deg 1..9):")
    for trial, coefs, bad_a1, P, fe_o, fo_o in polys:
        signed = [(c if c <= p//2 else c - p) for c in P]
        print(f"  Trial {trial} ({coefs}, |bad|={len(bad_a1)}): {signed[1:]}")  # skip constant which is 0

    # Trial 4 has 8 bad — check P degree
    print(f"\nTrial 4 has |bad|={len(polys[4][2])}, degree of P = {len(polys[4][3])-1}")


if __name__ == "__main__":
    main()
