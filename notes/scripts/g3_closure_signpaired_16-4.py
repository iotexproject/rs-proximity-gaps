"""g3_closure_signpaired_16-4.py — Groebner closure for sign-paired (16, 4, 4, 12).

Test if the locator divisor + certificate equations FORCE coset-rigid form
P(x) = x^8 + p_4 x^4 + p_0 (i.e., p_1 = p_2 = p_3 = p_5 = p_6 = p_7 = 0).

If the closure ideal contains (p_5, p_6, p_7), this proves coset-rigidity
symbolically.
"""
import sympy as sp


def main():
    x = sp.Symbol("x")
    p = sp.symbols("p0:8")
    rho = sp.Symbol("rho")
    n, k = 16, 4
    a, b = 4, 12
    t = n // 2  # 8

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    # Certificate equations: (rho * z^a + z^b) high coefficients (deg k..t-1) vanish
    cert_eqs = []
    for d in range(k, t):
        eq = sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        cert_eqs.append(eq)

    print(f"Certificate equations (deg {k}..{t-1}):")
    for d, eq in zip(range(k, t), cert_eqs):
        print(f"  deg {d}: {eq}")

    # Divisor equations: x^n - 1 mod P = 0
    div_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]
    print(f"\n{len(div_eqs)} divisor equations.")

    # Compute Groebner basis with elimination order: prioritize p_1, p_2, p_3, p_5, p_6, p_7
    # to see if these are forced to zero
    print("\nComputing Groebner basis (lex order, eliminating p variables)...")
    all_eqs = cert_eqs + div_eqs
    # Use lex order on (p, rho)
    G = sp.groebner(all_eqs, *p, rho, order="lex")
    print(f"Basis has {len(G.polys)} polynomials.")

    # Print rho-only polynomials
    print("\nrho-only polynomials in basis:")
    for poly in G.polys:
        expr = sp.factor(poly.as_expr())
        if not any(expr.has(var) for var in p) and expr != 0:
            deg = sp.Poly(expr, rho).degree()
            print(f"  deg {deg}: {expr}")

    # Print polynomials in a single p variable + rho
    print("\nUnivariate-in-p (after rho) polynomials:")
    for poly in G.polys:
        expr = poly.as_expr()
        nonzero_p = [v for v in p if expr.has(v)]
        if len(nonzero_p) == 1:
            print(f"  in {nonzero_p[0]}: {sp.factor(expr)}")

    # Check if p_5, p_6, p_7 are in the ideal (i.e., forced to 0)
    print("\n=== Coset-rigidity check ===")
    for var in [p[1], p[2], p[3], p[5], p[6], p[7]]:
        # var ∈ ideal iff reduce(var, G) == 0
        red = sp.reduced(var, list(G.polys), *p, rho, order="lex")[1]
        in_ideal = (red == 0)
        print(f"  {var} ∈ ideal (forced 0)?  {in_ideal}    (reduced to {red})")


if __name__ == "__main__":
    main()
