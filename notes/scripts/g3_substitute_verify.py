"""g3_substitute_verify.py — verify ONE DIRECTION of basis match via substitution.

If the closure pattern is:
  p_i = 0 for i ∉ {0, k}
  p_0 = ρ³
  p_k² = ρ³ - ρ
  ρ⁴ = 1
then substituting these into each cert+div equation should give 0
(in the appropriate quotient ring).

This verifies cert+div ⊆ I (where I is the proposed ideal).

It does NOT prove I ⊆ cert+div, but is one half. The other half is what
Sympy Groebner verifies; this gives us a sanity check that scales.
"""
import sys, time
import sympy as sp


def get_eqs(n, k, a, b):
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(n // 2))
    rho = sp.Symbol("rho")
    t = n // 2

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        for d in range(k, t)
    ]
    div_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]
    return cert_eqs, div_eqs, p, rho


def substitute_and_check(n, k, a, b):
    print(f"\n=== (n={n}, k={k}, a={a}, b={b}) substitute & check ===")
    cert_eqs, div_eqs, p, rho = get_eqs(n, k, a, b)
    t = n // 2

    # Substitution dict:
    #   p_i = 0 for i ∉ {0, k}
    #   p_0 = ρ³
    # Note: leave p_k as symbol — closure constraint p_k² = ρ³ - ρ handled separately
    subs = {p[i]: 0 for i in range(t) if i not in {0, k}}
    subs[p[0]] = rho**3

    p_k = p[k]

    fails_cert = 0
    fails_div = 0

    for i, eq in enumerate(cert_eqs):
        eq_sub = sp.simplify(eq.subs(subs))
        # Now eq_sub is in (ρ, p_k). Reduce modulo {p_k² - ρ³ + ρ, ρ⁴ - 1}
        # First reduce powers of p_k > 1
        eq_sub = sp.expand(eq_sub)
        # Replace p_k² → ρ³ - ρ (and higher powers via p_k²ⁿ⁺¹ = p_k · (ρ³-ρ)ⁿ etc.)
        # Brute force: collect poly in p_k, reduce
        pp = sp.Poly(eq_sub, p_k)
        coeffs = pp.all_coeffs()  # highest degree first
        # Reduce: p_k^j for j >= 2: replace recursively p_k² = ρ³ - ρ
        # Build sum: coeffs[i] * p_k^(deg-i)
        reduced = sp.Integer(0)
        for ci, c in enumerate(coeffs):
            j = len(coeffs) - 1 - ci  # degree of p_k
            # p_k^j: even j → (ρ³-ρ)^(j/2), odd j → p_k · (ρ³-ρ)^((j-1)/2)
            if j % 2 == 0:
                term = c * (rho**3 - rho)**(j // 2)
            else:
                term = c * p_k * (rho**3 - rho)**(j // 2)
            reduced += term
        # Now reduced is linear in p_k, with rho-only coefficient
        # Reduce ρ⁴ → 1 using sp.rem
        reduced = sp.expand(reduced)
        # Express as polynomial in ρ, take mod ρ⁴ - 1
        rho_poly = sp.Poly(reduced, p_k, rho)
        # Reduce each coefficient mod ρ⁴ - 1
        # Easier: substitute ρ⁴ = 1 by reducing ρ-degree
        for j in range(20, 3, -1):  # reduce ρ^j → ρ^(j-4)
            reduced = sp.expand(reduced.subs(rho**j, rho**(j-4)))
        # Also ρ⁴ → 1 specifically
        reduced = sp.expand(reduced)
        rho_poly = sp.Poly(reduced, rho)
        # Use rem
        reduced_mod = sp.rem(reduced, rho**4 - 1, rho)
        reduced_mod = sp.expand(reduced_mod)

        # Apply p_k(ρ²+1) = 0 rule: any term with p_k · (ρ² + 1) factor vanishes
        # I.e., reduce modulo p_k * (rho² + 1) in F_q[p_k, rho]
        # Equivalently: substitute ρ² → -1 in the COEFFICIENT of p_k
        rd = sp.Poly(reduced_mod, p_k)
        if rd.degree() <= 1:
            const_part = rd.coeff_monomial(1)
            pk_coeff = rd.coeff_monomial(p_k)
            # pk_coeff * p_k vanishes if pk_coeff is divisible by (ρ² + 1)
            # i.e., pk_coeff(ρ = ±i) = 0, equivalently sp.rem(pk_coeff, ρ² + 1) = 0
            pk_residual = sp.rem(pk_coeff, rho**2 + 1, rho)
            if const_part == 0 and pk_residual == 0:
                reduced_mod = 0
            else:
                reduced_mod = const_part + sp.expand(pk_residual * p_k)
        if reduced_mod != 0:
            fails_cert += 1
            if fails_cert <= 3:
                print(f"  cert eq[{i}] (deg {k+i}) does NOT vanish: residue = {reduced_mod}")

    for i, eq in enumerate(div_eqs):
        eq_sub = sp.simplify(eq.subs(subs))
        eq_sub = sp.expand(eq_sub)
        pp = sp.Poly(eq_sub, p_k)
        coeffs = pp.all_coeffs()
        reduced = sp.Integer(0)
        for ci, c in enumerate(coeffs):
            j = len(coeffs) - 1 - ci
            if j % 2 == 0:
                term = c * (rho**3 - rho)**(j // 2)
            else:
                term = c * p_k * (rho**3 - rho)**(j // 2)
            reduced += term
        reduced = sp.expand(reduced)
        for j in range(20, 3, -1):
            reduced = sp.expand(reduced.subs(rho**j, rho**(j-4)))
        reduced_mod = sp.rem(reduced, rho**4 - 1, rho)
        reduced_mod = sp.expand(reduced_mod)

        # Same p_k(ρ²+1) reduction
        rd = sp.Poly(reduced_mod, p_k)
        if rd.degree() <= 1:
            const_part = rd.coeff_monomial(1)
            pk_coeff = rd.coeff_monomial(p_k)
            pk_residual = sp.rem(pk_coeff, rho**2 + 1, rho)
            if const_part == 0 and pk_residual == 0:
                reduced_mod = 0
            else:
                reduced_mod = const_part + sp.expand(pk_residual * p_k)
        if reduced_mod != 0:
            fails_div += 1
            if fails_div <= 3:
                print(f"  div eq[{i}] does NOT vanish: residue = {reduced_mod}")

    if fails_cert == 0 and fails_div == 0:
        print(f"  ✓ ALL {len(cert_eqs)} cert eqs and {len(div_eqs)} div eqs vanish")
        print(f"  ✓ Direction (cert+div ⊆ proposed-ideal) verified")
        return True
    else:
        print(f"  FAIL: cert {fails_cert}/{len(cert_eqs)}, div {fails_div}/{len(div_eqs)}")
        return False


def main():
    cases = [
        (8, 2, 2, 6),
        (8, 2, 3, 7),
        (16, 4, 4, 12),
        (16, 4, 5, 13),
        (16, 4, 6, 14),
        (16, 4, 7, 15),
        (32, 8, 8, 24),
        (32, 8, 9, 25),
        (32, 8, 15, 31),
        (64, 16, 16, 48),
    ]
    results = []
    for n, k, a, b in cases:
        try:
            t0 = time.time()
            ok = substitute_and_check(n, k, a, b)
            dt = time.time() - t0
            results.append((n, k, a, b, ok, dt))
            print(f"  ({dt:.1f}s)")
        except Exception as e:
            print(f"  EXCEPTION: {type(e).__name__}: {e}")
            results.append((n, k, a, b, False, -1))
    print("\n=== Summary ===")
    for n, k, a, b, ok, dt in results:
        print(f"  ({n}, {k}, {a}, {b}): {'✓' if ok else 'FAIL'} ({dt:.1f}s)")


if __name__ == "__main__":
    main()
