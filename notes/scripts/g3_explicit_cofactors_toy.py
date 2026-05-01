"""g3_explicit_cofactors_toy.py — extract explicit ideal-membership cofactors.

For (8, 2, 2, 6) sign-paired, the GB output is:
  p_0 - ρ³, p_1, p_2² - ρ³ + ρ, p_2(ρ²+1), p_3, ρ⁴ - 1

Each is in the ideal cert+div. Want EXPLICIT polynomial combinations:
  GB_i = sum_j h_{ij} · (cert+div_j)

If the cofactor structure has a k-uniform pattern, we can lift to all k.

This script:
1. Computes cert+div generators at (8, 2, 2, 6).
2. For each GB generator, finds the cofactor combination via Sympy reduce.
3. Prints the cofactors with structural annotations.
"""
import time
import sympy as sp


def get_cert_div(n, k, a, b):
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(2 * k))
    rho = sp.Symbol("rho")
    t = 2 * k

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = []
    for d in range(k, t):
        coef_a = rem_a.coeff_monomial(x**d)
        coef_b = rem_b.coeff_monomial(x**d)
        cert_eqs.append((f"cert[{d}]", sp.expand(rho * coef_a + coef_b)))

    rem_n = sp.Poly(sp.rem(x**n - 1, P, x), x)
    coeffs = rem_n.all_coeffs()
    deg_x = rem_n.degree()
    div_eqs = []
    for i, c in enumerate(coeffs):
        # all_coeffs returns highest first
        d = deg_x - i
        div_eqs.append((f"div[{d}]", sp.expand(c)))

    return cert_eqs, div_eqs, p, rho


def main():
    n, k, a, b = 8, 2, 2, 6
    print(f"=== (n={n}, k={k}, a={a}, b={b}) sign-paired ===\n")
    cert_eqs, div_eqs, p, rho = get_cert_div(n, k, a, b)
    print("CERT EQUATIONS:")
    for name, eq in cert_eqs:
        print(f"  {name} = {eq}")
    print("\nDIV EQUATIONS:")
    for name, eq in div_eqs:
        print(f"  {name} = {eq}")
    print()

    eqs = [e for _, e in cert_eqs + div_eqs if e != 0]
    eq_names = [n for n, e in cert_eqs + div_eqs if e != 0]
    print(f"Total nonzero generators: {len(eqs)}\n")

    # Compute Groebner with the order
    G = sp.groebner(eqs, *p, rho, order="lex")
    print("LEX GB:")
    for i, g in enumerate(G):
        print(f"  G[{i}] = {g}")
    print()

    # For each GB element, try to express as combination
    # Sympy's Poly.div / reduce can do this
    print("EXPLICIT COFACTOR EXTRACTION:")
    print("(For each G[i], find h_j such that G[i] = sum_j h_j · eq_j)")
    print()

    target = G[-1]  # ρ⁴ - 1
    print(f"Target G[{len(G)-1}] = {target}")
    # Use sp.reduced
    quotient_list, remainder = sp.reduced(target, eqs, *p, rho)
    print(f"  remainder = {remainder}")
    print(f"  cofactors:")
    for j, q in enumerate(quotient_list):
        if q != 0:
            print(f"    h[{eq_names[j]}] = {q}")


if __name__ == "__main__":
    main()
